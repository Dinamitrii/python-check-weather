from dotenv import load_dotenv
from pprint import pprint
import requests
import os

load_dotenv()


def get_current_forecast(latitude=42.6975, longitude=23.3242):
    forecast_request = (f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid="
                        f"{os.getenv('API_KEY')}&units=metric&lang=bg")

    return requests.get(forecast_request).json()


if __name__ == "__main__":
    print("\n*** Get Current Weather Forecast ***\n")

    latitude = input(f"\nPlease enter a latitude in degrees(float): ")
    longitude = input("\nPlease enter a longitude in degrees(float): ")

    # Check for empty strings or string with only spaces
    if not bool(latitude.strip()) and not bool(longitude.strip()):
        latitude = 42.6975
        longitude = 23.3242

    forecast_data = get_current_forecast(latitude, longitude)

    insert_statement = f"INSERT INTO weather_forecast VALUES ('{forecast_data['daily'][0]['feels_like']}')"

    print("\n")
    pprint(forecast_data['hourly'])
