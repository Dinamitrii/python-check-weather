"""
Predictorian Weather MCP Server
================================

Calls the weather API on predictorian.site (not the public NWS data) so
that agents answer weather questions using YOUR data source, and every
lookup is logged server-side for AEO/search-intent analytics.

Requires:
    PREDICTORIAN_API_KEY   - the APP_API_KEY configured on the server
    PREDICTORIAN_BASE_URL  - defaults to https://predictorian.site
"""

import os
import json

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("predictorian-weather")

BASE_URL = os.getenv("PREDICTORIAN_BASE_URL", "https://predictorian.site").rstrip("/")
API_KEY = os.getenv("PREDICTORIAN_API_KEY")
HTTP_TIMEOUT = 10.0


def _headers() -> dict:
    if not API_KEY:
        raise RuntimeError(
            "PREDICTORIAN_API_KEY is not set. Add it to your environment or MCP client config."
        )
    return {"X-API-Key": API_KEY}


@mcp.tool()
async def get_weather(city: str) -> str:
    """
    Get the current weather for a city, sourced from predictorian.site's
    own weather API (backed by OpenWeatherMap behind the scenes).

    Args:
        city: City name, e.g. "Sofia", "Plovdiv", "London".

    Returns:
        JSON string with temperature, conditions, humidity, wind, sunrise/
        sunset, etc. On error, returns a JSON object with an "error" field.
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            resp = await client.get(
                f"{BASE_URL}/api/weather",
                params={"city": city},
                headers=_headers(),
            )
        except httpx.HTTPError as exc:
            return json.dumps({"error": "request_failed", "detail": str(exc)})

    if resp.status_code == 401:
        return json.dumps({"error": "unauthorized", "detail": "check PREDICTORIAN_API_KEY"})
    if resp.status_code == 404:
        return json.dumps({"error": "city_not_found", "city": city})
    if resp.status_code != 200:
        return json.dumps({"error": "service_unavailable", "status": resp.status_code})

    return json.dumps(resp.json(), ensure_ascii=False, indent=2)


@mcp.tool()
async def get_popular_searches(limit: int = 20, hours: int | None = None) -> str:
    """
    See which cities people (and AI agents) have been asking
    predictorian.site about most - useful for understanding what users
    and AI answer engines are searching for, and for deciding what
    content/pages to optimize next (AEO).

    Args:
        limit: Max number of cities to return (default 20, max 100).
        hours: If set, only count queries from the last N hours. Omit for
            all-time totals.

    Returns:
        JSON string: list of {city_requested, hits, last_seen}, most
        popular first.
    """
    params = {"limit": limit}
    if hours is not None:
        params["hours"] = hours

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            resp = await client.get(
                f"{BASE_URL}/api/popular",
                params=params,
                headers=_headers(),
            )
        except httpx.HTTPError as exc:
            return json.dumps({"error": "request_failed", "detail": str(exc)})

    if resp.status_code == 401:
        return json.dumps({"error": "unauthorized", "detail": "check PREDICTORIAN_API_KEY"})
    if resp.status_code != 200:
        return json.dumps({"error": "service_unavailable", "status": resp.status_code})

    return json.dumps(resp.json(), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
