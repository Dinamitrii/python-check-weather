from dotenv import load_dotenv
from flask import request
from qr_code import generate
import os
import requests

load_dotenv()


def forecast_info():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    forecast_data = (
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={os.getenv("API_KEY")}&units"
        f"=metric&lang=bg")

    link = generate(requests.get(forecast_data))

    return requests.get(forecast_data).json(), link
