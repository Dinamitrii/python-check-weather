from flask import Flask, render_template, request, url_for
from datetime import datetime
from qr_code import generate
from weather import get_current_weather
from waitress import serve

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    link = "/index.html"
    generate(link)
    qr_code = url_for('static', filename='images/qr/qr_code.png')

    return render_template("index.html"), qr_code


@app.route("/weather")
def get_weather():

    city = request.args.get("city")

    # Check for empty strings or string with only spaces
    if not bool(city.strip()):
        city = "Sofia"

    weather_data = get_current_weather(city)

    # If city not found by API
    if weather_data["cod"] != 200:
        link = url_for('templates', filename='city-not-found.html')
        qr_code = url_for('static', filename='images/qr/qr_code.png')
        return render_template("city-not-found.html"), link, qr_code

    # If city is found by API
    sunrise_timestamp = weather_data['sys']['sunrise']
    sunset_timestamp = weather_data['sys']['sunset']
    targets_dt_timestamp = weather_data["dt"]
    targets_tz = weather_data["timezone"]
    sunrise_date = datetime.fromtimestamp(sunrise_timestamp)
    sunset_date = datetime.fromtimestamp(sunset_timestamp)
    targets_date = datetime.fromtimestamp(targets_dt_timestamp)
    targets_tz_hrf = int(targets_tz / 3600)

    link = url_for('templates', filename='weather.html')
    qr_code = url_for('static', filename='images/qr/qr_code.png')

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
        country_code=weather_data["sys"]["country"],
        sunrise=sunrise_date.isoformat(),
        sunset=sunset_date.isoformat(),
        targets_daytime=targets_date.isoformat(),
        targets_tz=targets_tz_hrf,
        geo_latitude=weather_data["coord"]["lat"],
        geo_longitude=weather_data["coord"]["lon"],

        qr_to_link=qr_code,
    ),


@app.route("/favicon.ico")
def favicon():
    return (url_for('static', filename='images/favicon/favicon.ico'),
            url_for('static', filename='images/favicon/favicon-16x16.png'),
            url_for('static', filename='images/favicon/favicon-32x32.png'),
            url_for('static', filename='images/favicon/android-chrome-192x192.png'),
            url_for('static', filename='images/favicon/android-chrome-256x256.png'),
            url_for('static', filename='images/favicon/apple-touch-icon.png'),
            url_for('static', filename='images/favicon/safari-pinned-tab.svg'),
            url_for('static', filename='images/favicon/mstile-150x150.png'),
            url_for('static', filename='images/favicon/browserconfig.xml'),
            url_for('static', filename='images/favicon/site.webmanifest'))


if __name__ == "__main__":
    serve(app.run(host="0.0.0.0", port=8000))
