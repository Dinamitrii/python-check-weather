from dotenv import load_dotenv
from pprint import pprint
import requests
import os

load_dotenv()


def get_current_forecast(lat=42.6975, lon=23.3242):
    forecast_request = (f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid="
                        f"{os.getenv('API_KEY')}&units=metric&lang=bg")

    return requests.get(forecast_request).json()


get_current_forecast(lat=42.6975, lon=23.3242)

print("\n*** Get Current Weather Forecast ***\n")

latitude = input(f"\nPlease enter a latitude in degrees(float): ")
longitude = input("\nPlease enter a longitude in degrees(float): ")


# Check for empty strings or string with only spaces
if not latitude == "" and not longitude == "":

    lat = float(latitude)
    lon = float(longitude)


else:
    lat = float(42.6975)
    lon = float(23.3242)

    # if latitude is None and longitude is None:
    #     lat, lon = 42.6975, 23.3242

    forecast_data = get_current_forecast(lat, lon)

    print("\n")
    pprint(forecast_data)
