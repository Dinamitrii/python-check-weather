from flask import Flask, render_template, request
from weather import get_current_weather
from waitress import serve
from _datetime import datetime

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/weather")
def get_weather():
    city = request.args.get("city")

    # Check for empty strings or string with only spaces
    if not bool(city.strip()):
        city = "Sofia"

    weather_data = get_current_weather(city)

    # Getting local datetime and corresponding timestamp
    now_localized_readable = datetime.now()
    now_localized_timestamp = datetime.timestamp(now_localized_readable)

    # If city not found by API
    if weather_data["cod"] != 200:
        return render_template("city-not-found.html")

    # If city is found by API
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
        sunrise=weather_data["sys"]["sunrise"],
        sunset=weather_data["sys"]["sunset"],
        targets_daytime=weather_data["dt"],
        targets_tz=weather_data["timezone"],
        geo_latitude=weather_data["coord"]["lat"],
        geo_longitude=weather_data["coord"]["lon"],
    )


if __name__ == "__main__":
    serve(app.run(host="0.0.0.0"))
