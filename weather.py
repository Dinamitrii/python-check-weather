import os
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_current_weather(city="Sofia"):
    params = {
        "appid": os.getenv("API_KEY"),
        "q": city,
        "lang": "bg",
        "units": "metric",
    }
    try:
        response = requests.get(API_URL, params=params, timeout=5)
        return response.json()
    except (requests.RequestException, ValueError):
        # Network problem or bad JSON -> treated as "not found" by the caller
        return {"cod": 500}


if __name__ == "__main__":
    print("\n*** Get Current Weather Conditions ***\n")
    city = input("\nPlease enter a city name: ").strip() or "Sofia"
    print("\n")
    pprint(get_current_weather(city))
