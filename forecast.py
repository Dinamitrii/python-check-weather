from dotenv import load_dotenv
from pprint import pprint
import os
import requests

load_dotenv()


def forecast_info():

    forecast_url = (
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={os.getenv("API_KEY")}&units"
        f"=metric&lang=bg")

    return requests.get(forecast_url).json()


if __name__ == '__main__':
    print("\n*** Get Weather Forecast Info ***\n")

    lat = input("\nPlease enter a latitude: ")
    lon = input("\nPlease enter a longitude: ")

    forecast_data = forecast_info()

    print("\n")
    pprint(forecast_data)
