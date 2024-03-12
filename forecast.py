from dotenv import load_dotenv
from pprint import pprint
import requests
import os

load_dotenv()


def get_current_forecast(lat, lon):
    forecast_request = (f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid="
                        f"{os.getenv('API_KEY')}&units=metric&lang=bg")

    return requests.get(forecast_request).json()


if __name__ == "__main__":

    print("\n*** Get Current Weather Forecast ***")

    latitude = float(input("\nPlease enter a latitude in degrees: "))
    longitude = float(input("\nPlease enter a longitude in degrees: "))

    # here TO DO:
    # if emtpy string is given or some gibberish to give output for default location Sofia

    forecast_data = get_current_forecast(latitude, longitude)

    print("\n")
    pprint(forecast_data)
