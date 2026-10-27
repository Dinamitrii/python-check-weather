"""
JSON API for predictorian.site, meant for machine clients (the AEO MCP
server, other agents/integrations) rather than the human-facing /weather
HTML page.

Endpoints:
    GET /api/weather?city=Sofia         -> current weather as JSON
    GET /api/popular?limit=20&hours=24  -> most-searched cities (AEO insight)

Both require the header:  X-API-Key: <APP_API_KEY>
"""

import hmac
import os

from flask import Blueprint, jsonify, request

from api_logging import log_query, top_cities
from weather import get_current_weather

api = Blueprint("api", __name__, url_prefix="/api")

# MAX_CITY_LEN = 100


def _valid_api_key() -> bool:
    expected = os.getenv("APP_API_KEY")
    if not expected:
        # Fail closed: if no key is configured, the API is disabled rather
        # than silently open.
        return False
    provided = request.headers.get("X-API-Key", "")
    return hmac.compare_digest(provided, expected)


@api.before_request
def _require_api_key():
    if not _valid_api_key():
        return jsonify({"error": "unauthorized", "message": "missing or invalid X-API-Key header"}), 401


@api.get("/weather")
def api_weather():
    city = (request.args.get("city") or "").strip() or "Sofia"
    weather_data = get_current_weather(city)
    cod = weather_data.get("cod")

    resolved_name = weather_data.get("name") if cod == 200 else None
    country = weather_data.get("sys", {}).get("country") if cod == 200 else None

    log_query(
        city_requested=city,
        city_resolved=resolved_name,
        country=country,
        cod=cod,
        user_agent=request.headers.get("User-Agent"),
        client_ip=request.headers.get("X-Forwarded-For", request.remote_addr),
    )

    if cod == 404:
        return jsonify({"error": "city_not_found", "city": city}), 404
    if cod != 200:
        return jsonify({"error": "service_unavailable", "city": city, "detail": weather_data.get("message")}), 503

    main = weather_data["main"]
    return jsonify(
        {
            "city": weather_data["name"],
            "country": weather_data["sys"].get("country", ""),
            "coordinates": {
                "lat": weather_data["coord"]["lat"],
                "lon": weather_data["coord"]["lon"],
            },
            "conditions": weather_data["weather"][0]["description"],
            "temperature_c": round(main["temp"], 1),
            "temperature_min_c": round(main["temp_min"], 1),
            "temperature_max_c": round(main["temp_max"], 1),
            "feels_like_c": round(main["feels_like"], 1),
            "humidity_pct": main["humidity"],
            "pressure_hpa": main["pressure"],
            "wind_speed_ms": round(weather_data["wind"]["speed"], 1),
            "sunrise_utc": weather_data["sys"]["sunrise"],
            "sunset_utc": weather_data["sys"]["sunset"],
            "observed_at_utc": weather_data["dt"],
            "timezone_offset_s": weather_data["timezone"],
        }
    )


@api.get("/popular")
def api_popular():
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
    except ValueError:
        limit = 20
    since_hours = request.args.get("hours")
    since_hours = int(since_hours) if since_hours and since_hours.isdigit() else None

    return jsonify({"top_cities": top_cities(limit=limit, since_hours=since_hours)})
