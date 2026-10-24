import os
import threading
import time
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.openweathermap.org/data/2.5/weather"
CACHE_TTL = 600  # seconds
_CACHE_MAX = 500

_cache = {}
_lock = threading.Lock()


def _cache_get(key):
    with _lock:
        item = _cache.get(key)
        if item and time.monotonic() - item[0] < CACHE_TTL:
            return item[1]
        _cache.pop(key, None)
    return None


def _cache_set(key, value):
    with _lock:
        if len(_cache) >= _CACHE_MAX:
            _cache.clear()
        _cache[key] = (time.monotonic(), value)


def get_current_weather(city="Sofia"):
    """Return the OpenWeather payload with an int ``cod``.

    cod 200 -> success, 404 -> city not found, anything else -> service problem
    (bad key, quota exceeded, network error...).
    """
    key = city.casefold()
    cached = _cache_get(key)
    if cached is not None:
        return cached

    api_key = os.getenv("API_KEY")
    if not api_key:
        return {"cod": 500, "message": "API_KEY is not configured"}

    params = {"appid": api_key, "q": city, "lang": "bg", "units": "metric"}
    try:
        response = requests.get(API_URL, params=params, timeout=5)
        data = response.json()
    except (requests.RequestException, ValueError):
        return {"cod": 502, "message": "weather service unavailable"}

    try:
        data["cod"] = int(data.get("cod", response.status_code))
    except (TypeError, ValueError):
        data["cod"] = response.status_code

    if data["cod"] in (200, 404):
        _cache_set(key, data)
    return data


if __name__ == "__main__":
    print("\n*** Get Current Weather Conditions ***\n")
    city = input("\nPlease enter a city name: ").strip() or "Sofia"
    print("\n")
    pprint(get_current_weather(city))
