import json
from workers import WorkerEntrypoint, Response, fetch

# По подразбиране: София
DEFAULT_LAT, DEFAULT_LON = 42.6977, 23.3219

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(request.url).query)
        lat = q.get("lat", [DEFAULT_LAT])[0]
        lon = q.get("lon", [DEFAULT_LON])[0]

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )
        resp = await fetch(url)
        data = await resp.json()
        return Response(
            json.dumps(data["current_weather"]),
            headers={"content-type": "application/json"},
        )
