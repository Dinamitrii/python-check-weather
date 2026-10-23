from datetime import datetime, timezone, timedelta
from urllib.parse import quote

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory
from waitress import serve

load_dotenv()

from weather import get_current_weather
from qr_code_generator import link_to_qr_code

BASE_URL = "https://www.predictorian.online"

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    link_to_qr_code(f"{BASE_URL}/index")
    return render_template("index.html")


@app.route("/weather")
def get_weather():
    # Empty field or missing parameter -> Sofia
    city = (request.args.get("city") or "").strip() or "Sofia"

    link_to_qr_code(f"{BASE_URL}/weather?city={quote(city)}")

    weather_data = get_current_weather(city)

    # City not found (or API problem)
    if weather_data.get("cod") != 200:
        return render_template("city-not-found.html")

    # Times in the target city's own timezone, not the server's
    tz = timezone(timedelta(seconds=weather_data["timezone"]))
    sunrise_date = datetime.fromtimestamp(weather_data["sys"]["sunrise"], tz)
    sunset_date = datetime.fromtimestamp(weather_data["sys"]["sunset"], tz)
    targets_date = datetime.fromtimestamp(weather_data["dt"], tz)

    return render_template(
        "weather.html",
        title=weather_data["name"],
        status=weather_data["weather"][0]["description"].capitalize(),
        temp=f"{weather_data['main']['temp']:.1f}",
        temp_min=f"{weather_data['main']['temp_min']:.1f}",
        temp_max=f"{weather_data['main']['temp_max']:.1f}",
        feels_like=f"{weather_data['main']['feels_like']:.1f}",
        humidity=f"{weather_data['main']['humidity']}",
        atmos_pressure=f"{weather_data['main']['pressure']}",
        wind=f"{weather_data['wind']['speed']:.1f}",
        country_code=weather_data["sys"].get("country", ""),
        sunrise=sunrise_date.isoformat(),
        sunset=sunset_date.isoformat(),
        targets_daytime=targets_date.isoformat(),
        targets_tz=int(weather_data["timezone"] / 3600),
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
    serve(app, host="0.0.0.0", port=8000)
