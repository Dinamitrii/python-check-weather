import pytest

import server
import weather

SAMPLE = {
    "cod": 200,
    "name": "Sofia",
    "timezone": 7200,
    "dt": 1761300000,
    "coord": {"lat": 42.69, "lon": 23.32},
    "weather": [{"description": "ясно"}],
    "main": {"temp": 12.34, "temp_min": 10.0, "temp_max": 14.0,
             "feels_like": 11.0, "humidity": 55, "pressure": 1015},
    "wind": {"speed": 3.2},
    "sys": {"country": "BG", "sunrise": 1761279000, "sunset": 1761318000},
}


@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    return server.app.test_client()


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'name="city"' in r.get_data(as_text=True)
    assert "data:image/png;base64" in r.get_data(as_text=True)


def test_weather_ok(client, monkeypatch):
    monkeypatch.setattr(server, "get_current_weather", lambda c, k=None: SAMPLE)
    r = client.get("/weather?city=Sofia")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "12.3" in html and "UTC+2" in html and "55%" in html


def test_empty_city_defaults_to_sofia(client, monkeypatch):
    seen = []
    monkeypatch.setattr(server, "get_current_weather", lambda c, k=None: seen.append(c) or SAMPLE)
    client.get("/weather?city=%20%20")
    assert seen == ["Sofia"]


def test_city_not_found(client, monkeypatch):
    monkeypatch.setattr(server, "get_current_weather", lambda c, k=None: {"cod": 404})
    assert client.get("/weather?city=zzz").status_code == 404


def test_service_error(client, monkeypatch):
    monkeypatch.setattr(server, "get_current_weather", lambda c, k=None: {"cod": 401})
    assert client.get("/weather?city=Sofia").status_code == 503


def test_city_is_escaped(client, monkeypatch):
    data = dict(SAMPLE, name="<script>alert(1)</script>")
    monkeypatch.setattr(server, "get_current_weather", lambda c, k=None: data)
    assert "<script>alert(1)</script>" not in client.get("/weather?city=x").get_data(as_text=True)


def test_half_hour_offset():
    assert server._format_offset(19800) == "UTC+5:30"
    assert server._format_offset(-18000) == "UTC-5"


def test_robots_and_sitemap(client):
    assert client.get("/robots.txt").status_code == 200
    assert client.get("/sitemap.xml").status_code == 200


def test_weather_client_missing_key(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    weather._cache.clear()
    assert weather.get_current_weather("Nowhere")["cod"] == 500


def test_weather_client_caches(monkeypatch):
    monkeypatch.setenv("API_KEY", "x")
    weather._cache.clear()
    calls = []

    class R:
        status_code = 200
        def json(self): return dict(SAMPLE)

    monkeypatch.setattr(weather.requests, "get", lambda *a, **k: calls.append(1) or R())
    weather.get_current_weather("Sofia"); weather.get_current_weather("SOFIA")
    assert len(calls) == 1
