from flask import Flask, render_template, request, url_for
from _datetime import datetime
from weather import get_current_weather
from waitress import serve
from qr_code_generator import link_to_qr_code
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    link_to_qr_code("https://www.predictorian.online/index")

    return render_template("index.html")


@app.route("/weather")
def get_weather():
    city = request.args.get("city")

    # Check for empty strings or string with only spaces
    if not bool(city.strip()):
        city = "Sofia"

    weather_data = get_current_weather(city)

    link_to_qr_code("https://www.predictorian.online/weather" + "?city=" + city)

    # If city not found by API
    if weather_data["cod"] != 200:
        link_to_qr_code("https://www.predictorian.online/weather" + "?city=" + city)

        return render_template("city-not-found.html")

    # If city is found by API
    sunrise_timestamp = weather_data['sys']['sunrise']
    sunset_timestamp = weather_data['sys']['sunset']
    targets_dt_timestamp = weather_data["dt"]
    targets_tz = weather_data["timezone"]
    sunrise_date = datetime.fromtimestamp(sunrise_timestamp)
    sunset_date = datetime.fromtimestamp(sunset_timestamp)
    targets_date = datetime.fromtimestamp(targets_dt_timestamp)
    targets_tz_human_readable_format = int(targets_tz / 3600)

    link_to_qr_code("https://www.predictorian.online/weather" + "?city=" + city)

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
        targets_tz=targets_tz_human_readable_format,
        geo_latitude=weather_data["coord"]["lat"],
        geo_longitude=weather_data["coord"]["lon"]
    )


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


@app.route('/sitemap.xml')
def sitemap():
    return url_for('static', filename='sitemap/sitemap.xml')


@app.route('/robots.txt')
def robots():
    return url_for("robots",filename='robots.txt')



if __name__ == "__main__":
    serve(app.run(host="0.0.0.0", port=8000))
