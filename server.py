import os

from flask import Flask, render_template, request
from weather import get_current_weather, get_current_forecast
from waitress import serve

app = Flask(__name__)


@app.route("/")
@app.route("/index/")
def index():
    return render_template("index.html")


@app.route("/weather/")
def get_weather():
    city = request.args.get("city")

    # Check for empty strings or string with only spaces
    if not bool(city.strip()):
        city = "Sofia"

    weather_data = get_current_weather(city)

    # If city not found by API
    if weather_data["cod"] != 200:
        return render_template("city-not-found.html")

    return render_template(
        "weather.html",
        title=weather_data["name"],
        status=weather_data["weather"][0]["description"].capitalize(),
        temp=f"{weather_data['main']['temp']:.1f}",
        temp_min=f"{weather_data['main']['temp_min']:.1f}",
        temp_max=f"{weather_data['main']['temp_max']:.1f}",
        feels_like=f"{weather_data['main']['feels_like']:.1f}",
        wind=f"{weather_data['wind']['speed']:.1f}",
        sea_level=f"{weather_data['main']['sea_level']:.2f}",
        humidity=f"{weather_data['main']['humidity']}",
        pressure=f"{weather_data['main']['pressure']}",
        country_code=f"{weather_data['sys']['country']}",
        geo_latitude=f"{weather_data['coord']['lat']}",
        geo_longitude=f"{weather_data['coord']['lon']}",
    )


@app.route("/forecast/")
def get_forecast():
    latitude = request.args.get("lat")
    longitude = request.args.get("lon")

    request_url = (f"https://api.openweathermap.org/data/3.0/onecall?{latitude}&{longitude}&appid"
                   f"={os.getenv('API_KEY')}")

    forecast_data = get_current_forecast()

    return render_template(
        "forecast.html",
                           )



if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
