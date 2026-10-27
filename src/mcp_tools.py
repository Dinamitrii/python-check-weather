"""Weather MCP tools: alerts and forecasts from api.weather.gov (NWS).

Runs both on Cloudflare Workers (Pyodide) and locally, mirroring the
dual fetch pattern already used in weather.py — Workers has no raw
sockets, so httpx/requests only work outside Workers.
"""
from typing import Any

try:  # Cloudflare Workers (Pyodide)
    from pyodide.ffi import run_sync
    from pyodide.http import pyfetch

    ON_WORKERS = True
except ImportError:  # local / uWSGI / Docker
    import requests

    ON_WORKERS = False

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "predictorian-weather-mcp/1.0 (+https://predictorian.site)"


def _nws_get(url: str) -> dict[str, Any] | None:
    """GET an NWS endpoint and return parsed JSON, or None on any failure."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    try:
        if ON_WORKERS:
            response = run_sync(pyfetch(url, headers=headers))
            if response.status >= 400:
                return None
            return run_sync(response.json())
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def _format_alert(feature: dict) -> str:
    props = feature["properties"]
    return (
        f"Event: {props.get('event', 'Unknown')}\n"
        f"Area: {props.get('areaDesc', 'Unknown')}\n"
        f"Severity: {props.get('severity', 'Unknown')}\n"
        f"Description: {props.get('description', 'No description available')}\n"
        f"Instructions: {props.get('instruction', 'No specific instructions provided')}"
    )


def get_alerts(state: str) -> str:
    """Active weather alerts for a two-letter US state code (e.g. CA, NY)."""
    state = (state or "").strip().upper()
    if len(state) != 2 or not state.isalpha():
        return "Invalid state code. Use a two-letter US state code, e.g. CA or NY."

    data = _nws_get(f"{NWS_API_BASE}/alerts/active/area/{state}")
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."
    return "\n---\n".join(_format_alert(f) for f in data["features"])


def get_forecast(latitude: float, longitude: float) -> str:
    """Next 5 forecast periods for a US location given its lat/long."""
    points = _nws_get(f"{NWS_API_BASE}/points/{latitude},{longitude}")
    if not points:
        return "Unable to fetch forecast data for this location."

    forecast_url = points.get("properties", {}).get("forecast")
    if not forecast_url:
        return "Unable to fetch forecast data for this location."

    forecast = _nws_get(forecast_url)
    if not forecast:
        return "Unable to fetch detailed forecast."

    periods = forecast["properties"]["periods"][:5]
    out = []
    for p in periods:
        out.append(
            f"{p['name']}:\n"
            f"Temperature: {p['temperature']}\u00b0{p['temperatureUnit']}\n"
            f"Wind: {p['windSpeed']} {p['windDirection']}\n"
            f"Forecast: {p['detailedForecast']}"
        )
    return "\n---\n".join(out)


# Tool registry consumed by mcp_routes.py (tools/list + tools/call).
TOOLS = {
    "get_alerts": {
        "description": "Get active weather alerts for a US state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "type": "string",
                    "description": "Two-letter US state code (e.g. CA, NY)",
                }
            },
            "required": ["state"],
        },
        "fn": get_alerts,
    },
    "get_forecast": {
        "description": "Get the weather forecast for a US location.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude of the location",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude of the location",
                },
            },
            "required": ["latitude", "longitude"],
        },
        "fn": get_forecast,
    },
}
