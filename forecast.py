from dotenv import load_dotenv
from pprint import pprint
import requests
import os

load_dotenv()


def get_current_forecast(latitude=42.6975, longitude=23.3242):
    forecast_request = (f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid="
                        f"{os.getenv('API_KEY')}&units=metric&lang=bg")

    return requests.get(forecast_request).json()

    # here TO DO:
    # if emtpy string is given or some gibberish to give output for default location Sofia


if __name__ == get_current_forecast(latitude=42.6975, longitude=23.3242):
    print("\n*** Get Current Weather Forecast ***\n")

    latitude = float(input("\nPlease enter a latitude in degrees(float): "))
    longitude = float(input("\nPlease enter a longitude in degrees(float): "))

    if latitude == 0 and longitude == 0:
        latitude, longitude = 42.6975, 23.3242

        forecast_data = get_current_forecast(latitude, longitude)

        print("\n")
        pprint(forecast_data)
