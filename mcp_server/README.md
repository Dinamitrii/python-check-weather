# AEO MCP Server

Custom MCP server for Answer Engine Optimization (AEO): checks whether your
brand shows up in AI-generated answers, audits a page's AEO readiness, and
compares your visibility against named competitors.

## Tools

| Tool | What it does |
|---|---|
| `check_ai_visibility(brand, query, engines?)` | Asks ChatGPT / Claude / Perplexity the query and reports whether `brand` appears in each answer. |
| `analyze_page_aeo(url)` | Audits a page: robots.txt access for AI crawlers, `llms.txt`, schema.org/JSON-LD, heading structure, answer-first opening paragraph. Returns findings + concrete recommendations. |
| `competitor_aeo_compare(brand, competitors, query, engines?)` | Runs the same query across engines and builds a leaderboard of which brand/competitor is mentioned most. |

## 1. Install

```bash
cd aeo-mcp-server
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Add your API keys

```bash
cp .env.example .env
```

Edit `.env` and fill in whichever keys you have:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
```

You don't need all three — any engine without a key is just skipped and
reported as `"status": "skipped"` in the tool output. `analyze_page_aeo`
needs no API key at all.

## 3. Run it standalone (for testing)

```bash
python server.py
```

This starts the server on stdio, waiting for an MCP client to connect.

## 4. Connect it to Claude Desktop

Open your Claude Desktop config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add an entry under `mcpServers` (adjust the path to where you placed this folder):

```json
{
  "mcpServers": {
    "aeo-server": {
      "command": "/absolute/path/to/aeo-mcp-server/.venv/bin/python",
      "args": ["/absolute/path/to/aeo-mcp-server/server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "PERPLEXITY_API_KEY": "pplx-..."
      }
    }
  }
}
```

Restart Claude Desktop. The three tools above will then be available to
Claude in any conversation.

## 5. Connect it to Claude Code

```bash
claude mcp add aeo-server -- /absolute/path/to/aeo-mcp-server/.venv/bin/python /absolute/path/to/aeo-mcp-server/server.py
```

## Notes / next steps

- `check_ai_visibility` and `competitor_aeo_compare` call the *live* chat
  completion APIs of OpenAI/Anthropic/Perplexity, so each call costs a small
  amount of API usage on your own account's keys.
- `analyze_page_aeo`'s robots.txt parsing is intentionally simple (regex-based
  per User-agent block). For complex robots.txt files, double check manually.
- Natural extension points if you want to grow this later: a Google/Gemini
  check via the Gemini API, caching of repeated queries, and a
  `track_visibility_over_time` tool that stores results to a local SQLite
  file so you can chart trends.
