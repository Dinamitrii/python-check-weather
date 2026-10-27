# Predictorian Weather MCP Server

MCP server that makes agents (Claude, etc.) fetch weather answers from
**your own** `predictorian.site` API instead of a generic weather source,
and logs every question so you can see what people are actually searching
for.

```
Agent (Claude) --MCP--> this server --HTTPS + X-API-Key--> predictorian.site/api/weather
                                                                      |
                                                                      v
                                                          query_log.sqlite3 (who asked what)
```

## 0. First: apply the server-side changes

Files to add/update in your `python-check-weather` repo are in
`predictorian-api-changes/`:

| File | Action |
|---|---|
| `api_routes.py` | **new file** - copy into repo root |
| `api_logging.py` | **new file** - copy into repo root |
| `server.py` | **modified** - either copy over yours, or apply `changes.diff` |
| `.env.example` | **modified** - adds `APP_API_KEY` |
| `.gitignore` | **modified** - ignores the new `query_log.sqlite3` |

To apply as a patch instead of copying files by hand:

```bash
cd python-check-weather
git apply /path/to/changes.diff
# then manually add api_routes.py and api_logging.py (new files aren't in the diff)
```

Then on your server:

```bash
# generate a real key - do NOT use the placeholder
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# put it in your real .env as APP_API_KEY=<that value>
```

Restart the Flask app (systemd service / whatever `weather.service` does).

**⚠️ Also rotate your OpenWeatherMap key.** The current one
(`f7e79c61...`) is permanently visible in your public GitHub repo's commit
history (`.env.example`, old commits), even though a later commit replaced
it with a placeholder. Generate a new key at openweathermap.org, update
`.env` on the server, and treat the old one as compromised.

## 1. New endpoints this adds

- `GET /api/weather?city=Sofia` - JSON weather, requires `X-API-Key` header
- `GET /api/popular?limit=20&hours=24` - most-asked-about cities, requires `X-API-Key` header

Every call to `/api/weather` is logged (city, resolved city/country,
timestamp, User-Agent, IP) to a local SQLite file (`query_log.sqlite3`),
so you can see which AI crawlers/agents (GPTBot, PerplexityBot, ClaudeBot,
etc. show up in User-Agent) are pulling your data, and what they're asking.

## 2. Install this MCP server

```bash
cd predictorian-weather-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure

```bash
export PREDICTORIAN_API_KEY="the APP_API_KEY you generated above"
export PREDICTORIAN_BASE_URL="https://predictorian.site"   # or http://localhost:8000 for local testing
```

## 4. Tools exposed

| Tool | What it does |
|---|---|
| `get_weather(city)` | Fetches current weather for a city via your API. |
| `get_popular_searches(limit?, hours?)` | Returns the most-asked-about cities - lets an agent (or you) see what users/AI engines have been searching for. |

## 5. Connect to Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "predictorian-weather": {
      "command": "/absolute/path/to/predictorian-weather-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/predictorian-weather-mcp/server.py"],
      "env": {
        "PREDICTORIAN_API_KEY": "...",
        "PREDICTORIAN_BASE_URL": "https://predictorian.site"
      }
    }
  }
}
```

## 6. Connect to Claude Code

```bash
claude mcp add predictorian-weather \
  --env PREDICTORIAN_API_KEY=... \
  --env PREDICTORIAN_BASE_URL=https://predictorian.site \
  -- /absolute/path/to/predictorian-weather-mcp/.venv/bin/python /absolute/path/to/predictorian-weather-mcp/server.py
```

## How this ties into AEO

The original `aeo-mcp-server` (separate project, built earlier) checks
whether your brand is *mentioned* when AI engines answer a query, and
audits a page's AEO readiness. This server is the other half: it's the
actual data channel an agent uses to answer a weather question using
*your* data, and the `get_popular_searches` tool turns your own traffic
into a signal for what to optimize content around next (e.g. if "Burgas"
is searched a lot but your Burgas page is thin, that's your next AEO
target).
