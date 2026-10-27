import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory

load_dotenv()

from api_routes import api as api_blueprint  # noqa: E402
from qr_code_generator import link_to_qr_code  # noqa: E402
from weather import get_current_weather  # noqa: E402

BASE_URL = os.getenv("BASE_URL", "https://predictorian.site").rstrip("/")
MAX_CITY_LEN = 100

app = Flask(__name__)
app.register_blueprint(api_blueprint)


def _format_offset(seconds: int) -> str:
    sign = "+" if seconds >= 0 else "-"
    minutes = abs(seconds) // 60
    hours, mins = divmod(minutes, 60)
    return f"UTC{sign}{hours}" + (f":{mins:02d}" if mins else "")


@app.route("/")
@app.route("/index")
def index():
    return render_template(
        "index.html",
        base_url=BASE_URL,
        qr_code=link_to_qr_code(f"{BASE_URL}/"),
    )


@app.route("/weather")
def get_weather():
    # Empty field or missing parameter -> Sofia
    city = (request.args.get("city") or "").strip()[:MAX_CITY_LEN] or "Sofia"
    qr_code = link_to_qr_code(f"{BASE_URL}/weather?city={quote(city)}")

    weather_data = get_current_weather(city)
    cod = weather_data.get("cod")

    if cod == 404:
        return (
            render_template("city-not-found.html", base_url=BASE_URL, qr_code=qr_code),
            404,
        )
    if cod != 200:
        return (
            render_template("service-error.html", base_url=BASE_URL, qr_code=qr_code),
            503,
        )

    offset = int(weather_data["timezone"])
    tz = timezone(timedelta(seconds=offset))

    def clock(ts):
        return datetime.fromtimestamp(ts, tz).strftime("%H:%M")

    main = weather_data["main"]
    return render_template(
        "weather.html",
        base_url=BASE_URL,
        qr_code=qr_code,
        title=weather_data["name"],
        status=weather_data["weather"][0]["description"].capitalize(),
        temp=f"{main['temp']:.1f}",
        temp_min=f"{main['temp_min']:.1f}",
        temp_max=f"{main['temp_max']:.1f}",
        feels_like=f"{main['feels_like']:.1f}",
        humidity=main["humidity"],
        atmos_pressure=main["pressure"],
        wind=f"{weather_data['wind']['speed']:.1f}",
        country_code=weather_data["sys"].get("country", ""),
        sunrise=clock(weather_data["sys"]["sunrise"]),
        sunset=clock(weather_data["sys"]["sunset"]),
        local_time=datetime.fromtimestamp(weather_data["dt"], tz).strftime(
            "%d.%m.%Y %H:%M"
        ),
        tz_label=_format_offset(offset),
        geo_latitude=weather_data["coord"]["lat"],
        geo_longitude=weather_data["coord"]["lon"],
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "images/favicon/favicon.ico")


@app.route("/robots.txt")
@app.route("/sitemap.xml")
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == "__main__":
    import logging

    from waitress import serve

    logging.basicConfig(level=logging.INFO)
    serve(app, host="0.0.0.0", port=8000)
