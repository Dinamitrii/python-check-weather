"""
AEO (Answer Engine Optimization) MCP Server
=============================================

Provides tools for:
  1. check_ai_visibility   - is a brand mentioned when AI engines answer a query?
  2. analyze_page_aeo      - is a web page structured well for AI answer engines?
  3. competitor_aeo_compare - compare AI-answer visibility of a brand vs competitors

Requires API keys (set as environment variables, see .env.example):
  OPENAI_API_KEY       (optional - enables ChatGPT visibility checks)
  ANTHROPIC_API_KEY    (optional - enables Claude visibility checks)
  PERPLEXITY_API_KEY   (optional - enables Perplexity visibility checks)

Any engine whose key is missing is simply skipped (reported as "skipped").
"""

import os
import re
import json
import asyncio
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("aeo-server")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")

AI_CRAWLER_USER_AGENTS = {
    "GPTBot": "OpenAI (ChatGPT browsing / training)",
    "ChatGPT-User": "OpenAI (ChatGPT plugin browsing)",
    "PerplexityBot": "Perplexity AI",
    "ClaudeBot": "Anthropic Claude",
    "anthropic-ai": "Anthropic (legacy)",
    "Google-Extended": "Google (Gemini / AI Overviews / Bard training)",
    "Bytespider": "ByteDance (TikTok / Doubao)",
    "CCBot": "Common Crawl (feeds many AI training sets)",
}

HTTP_TIMEOUT = 20.0


# ---------------------------------------------------------------------------
# Helpers: querying each AI engine
# ---------------------------------------------------------------------------

async def _ask_openai(query: str) -> str:
    if not OPENAI_API_KEY:
        return "__SKIPPED__"
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": query}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _ask_anthropic(query: str) -> str:
    if not ANTHROPIC_API_KEY:
        return "__SKIPPED__"
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 600,
                "messages": [{"role": "user", "content": query}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "\n".join(text_blocks)


async def _ask_perplexity(query: str) -> str:
    if not PERPLEXITY_API_KEY:
        return "__SKIPPED__"
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": query}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


ENGINE_FUNCS = {
    "openai": _ask_openai,
    "anthropic": _ask_anthropic,
    "perplexity": _ask_perplexity,
}


def _brand_mentioned(text: str, brand: str) -> bool:
    if not text or text == "__SKIPPED__":
        return False
    return re.search(re.escape(brand), text, re.IGNORECASE) is not None


async def _visibility_for_brand(brand: str, query: str, engines: list[str]) -> dict:
    """Ask each requested engine the query and check for brand mentions."""
    results = {}
    tasks = {name: ENGINE_FUNCS[name](query) for name in engines if name in ENGINE_FUNCS}
    responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for name, resp in zip(tasks.keys(), responses):
        if isinstance(resp, Exception):
            results[name] = {"status": "error", "error": str(resp)}
        elif resp == "__SKIPPED__":
            results[name] = {"status": "skipped", "reason": "missing API key"}
        else:
            mentioned = _brand_mentioned(resp, brand)
            results[name] = {
                "status": "ok",
                "mentioned": mentioned,
                "answer_excerpt": resp[:400],
            }
    return results


# ---------------------------------------------------------------------------
# Tool 1: AI visibility check
# ---------------------------------------------------------------------------

@mcp.tool()
async def check_ai_visibility(
    brand: str,
    query: str,
    engines: Optional[list[str]] = None,
) -> str:
    """
    Check whether a brand is mentioned when AI answer engines (ChatGPT,
    Claude, Perplexity) respond to a given query.

    Args:
        brand: Brand or company name to look for in the answers.
        query: The question to ask each AI engine (e.g. "best project
            management tools for small teams").
        engines: Which engines to query. Subset of ["openai", "anthropic",
            "perplexity"]. Defaults to all three (engines without a
            configured API key are reported as skipped).

    Returns:
        JSON string with one entry per engine: whether the brand was
        mentioned, and an excerpt of the answer.
    """
    engines = engines or ["openai", "anthropic", "perplexity"]
    results = await _visibility_for_brand(brand, query, engines)
    mentioned_count = sum(1 for r in results.values() if r.get("mentioned"))
    checked_count = sum(1 for r in results.values() if r.get("status") == "ok")
    summary = {
        "brand": brand,
        "query": query,
        "mentioned_in": f"{mentioned_count}/{checked_count}" if checked_count else "0/0 (no engines configured)",
        "engines": results,
    }
    return json.dumps(summary, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 2: Page AEO analysis
# ---------------------------------------------------------------------------

async def _fetch_text(client: httpx.AsyncClient, url: str) -> Optional[str]:
    try:
        resp = await client.get(url, timeout=HTTP_TIMEOUT, follow_redirects=True)
        if resp.status_code == 200:
            return resp.text
    except httpx.HTTPError:
        pass
    return None


@mcp.tool()
async def analyze_page_aeo(url: str) -> str:
    """
    Analyze a web page for Answer Engine Optimization (AEO) readiness:
    whether AI crawlers can access it, whether it carries structured data,
    and whether its content is shaped to be quoted directly in an AI answer.

    Args:
        url: Full URL of the page to analyze (e.g. "https://example.com/pricing").

    Returns:
        JSON string with a checklist of AEO signals and concrete
        recommendations.
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (AEO-Audit-Bot)"}) as client:
        page_html, robots_txt, llms_txt = await asyncio.gather(
            _fetch_text(client, url),
            _fetch_text(client, f"{origin}/robots.txt"),
            _fetch_text(client, f"{origin}/llms.txt"),
        )

    findings = {"url": url, "checks": {}, "recommendations": []}

    if not page_html:
        findings["checks"]["page_reachable"] = False
        findings["recommendations"].append("Page could not be fetched - check it is public and returns HTTP 200.")
        return json.dumps(findings, indent=2, ensure_ascii=False)

    findings["checks"]["page_reachable"] = True
    soup = BeautifulSoup(page_html, "html.parser")

    # --- robots.txt: are AI crawlers allowed? ---
    blocked_bots = []
    if robots_txt:
        for bot in AI_CRAWLER_USER_AGENTS:
            # naive check: a Disallow: / directly under this bot's User-agent block
            pattern = rf"User-agent:\s*{re.escape(bot)}.*?(?=User-agent:|\Z)"
            match = re.search(pattern, robots_txt, re.IGNORECASE | re.DOTALL)
            if match and re.search(r"Disallow:\s*/\s*$", match.group(0), re.IGNORECASE | re.MULTILINE):
                blocked_bots.append(bot)
    findings["checks"]["robots_txt_found"] = bool(robots_txt)
    findings["checks"]["ai_crawlers_blocked"] = blocked_bots
    if blocked_bots:
        findings["recommendations"].append(
            f"robots.txt blocks these AI crawlers: {', '.join(blocked_bots)}. "
            "Remove the Disallow rule if you want to be eligible for AI answers."
        )

    # --- llms.txt ---
    findings["checks"]["llms_txt_found"] = bool(llms_txt)
    if not llms_txt:
        findings["recommendations"].append(
            "No /llms.txt found. Consider adding one - a plain-text summary of your "
            "site's key pages helps AI systems understand and cite your content."
        )

    # --- JSON-LD structured data ---
    jsonld_scripts = soup.find_all("script", type="application/ld+json")
    schema_types = []
    for tag in jsonld_scripts:
        try:
            data = json.loads(tag.string or "{}")
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type")
                if t:
                    schema_types.append(t)
        except (json.JSONDecodeError, AttributeError):
            continue
    findings["checks"]["schema_org_types"] = schema_types
    if not schema_types:
        findings["recommendations"].append(
            "No schema.org JSON-LD found. Add structured data (Article, FAQPage, "
            "Product, Organization, etc.) so AI systems can parse facts reliably."
        )
    if "FAQPage" not in schema_types:
        findings["recommendations"].append(
            "No FAQPage schema detected. FAQ-formatted Q&A content is one of the "
            "most frequently quoted formats in AI answers."
        )

    # --- meta description ---
    meta_desc = soup.find("meta", attrs={"name": "description"})
    findings["checks"]["meta_description"] = meta_desc["content"] if meta_desc and meta_desc.get("content") else None

    # --- heading structure ---
    h1s = soup.find_all("h1")
    h2s = soup.find_all("h2")
    findings["checks"]["h1_count"] = len(h1s)
    findings["checks"]["h2_count"] = len(h2s)
    if len(h1s) != 1:
        findings["recommendations"].append(
            f"Page has {len(h1s)} <h1> tags (should be exactly 1) - a clear single "
            "H1 helps AI systems identify the page's main topic."
        )

    # --- answer-first paragraph check ---
    first_p = soup.find("p")
    first_p_text = first_p.get_text(strip=True) if first_p else ""
    findings["checks"]["first_paragraph_word_count"] = len(first_p_text.split())
    findings["checks"]["first_paragraph_excerpt"] = first_p_text[:200]
    if len(first_p_text.split()) < 15:
        findings["recommendations"].append(
            "First paragraph is very short. AI answer engines favor pages that state "
            "a direct, self-contained answer in the opening 1-2 sentences."
        )

    if not findings["recommendations"]:
        findings["recommendations"].append("No major issues found - page looks AEO-ready.")

    return json.dumps(findings, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 3: Competitor comparison
# ---------------------------------------------------------------------------

@mcp.tool()
async def competitor_aeo_compare(
    brand: str,
    competitors: list[str],
    query: str,
    engines: Optional[list[str]] = None,
) -> str:
    """
    Compare how often your brand vs. named competitors are mentioned when
    AI engines answer the same query.

    Args:
        brand: Your brand/company name.
        competitors: List of competitor brand/company names.
        query: The question to ask each AI engine (should be a query a
            prospective customer might actually type, e.g. "best CRM for
            small agencies").
        engines: Which engines to query. Subset of ["openai", "anthropic",
            "perplexity"]. Defaults to all three.

    Returns:
        JSON string: for each engine, the raw answer plus which of
        [brand + competitors] were mentioned in it. Includes a simple
        leaderboard by mention count.
    """
    engines = engines or ["openai", "anthropic", "perplexity"]
    tasks = {name: ENGINE_FUNCS[name](query) for name in engines if name in ENGINE_FUNCS}
    responses = await asyncio.gather(*tasks.values(), return_exceptions=True)

    all_names = [brand] + list(competitors)
    leaderboard = {name: 0 for name in all_names}
    per_engine = {}

    for engine_name, resp in zip(tasks.keys(), responses):
        if isinstance(resp, Exception):
            per_engine[engine_name] = {"status": "error", "error": str(resp)}
            continue
        if resp == "__SKIPPED__":
            per_engine[engine_name] = {"status": "skipped", "reason": "missing API key"}
            continue
        mentions = {name: _brand_mentioned(resp, name) for name in all_names}
        for name, was_mentioned in mentions.items():
            if was_mentioned:
                leaderboard[name] += 1
        per_engine[engine_name] = {
            "status": "ok",
            "mentions": mentions,
            "answer_excerpt": resp[:500],
        }

    ranked = sorted(leaderboard.items(), key=lambda kv: kv[1], reverse=True)
    result = {
        "query": query,
        "brand": brand,
        "competitors": competitors,
        "leaderboard": [{"name": n, "engines_mentioning": c} for n, c in ranked],
        "per_engine_detail": per_engine,
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
