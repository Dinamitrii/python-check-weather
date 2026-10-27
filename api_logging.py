"""
Lightweight query logging for /api/weather.

Every request is recorded so you can see, over time, which cities people
(and AI agents) are actually asking about - useful both as product
analytics and as an AEO signal (what questions are landing on your site
via AI answer engines).
"""

import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.getenv("QUERY_LOG_DB", os.path.join(os.path.dirname(__file__), "query_log.sqlite3"))

_lock = threading.Lock()
_initialized = False


def _init_db():
    global _initialized
    if _initialized:
        return
    with _lock:
        if _initialized:
            return
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                city_requested TEXT NOT NULL,
                city_resolved TEXT,
                country TEXT,
                cod INTEGER,
                user_agent TEXT,
                client_ip TEXT,
                via_api INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_query_log_city ON query_log(city_requested)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_query_log_ts ON query_log(ts)"
        )
        conn.commit()
        conn.close()
        _initialized = True


@contextmanager
def _connection():
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def log_query(
    city_requested: str,
    city_resolved: str | None = None,
    country: str | None = None,
    cod: int | None = None,
    user_agent: str | None = None,
    client_ip: str | None = None,
):
    """Record one weather lookup. Never raises - logging must not break the request."""
    try:
        with _connection() as conn, _lock:
            conn.execute(
                """
                INSERT INTO query_log
                    (ts, city_requested, city_resolved, country, cod, user_agent, client_ip)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    city_requested,
                    city_resolved,
                    country,
                    cod,
                    user_agent,
                    client_ip,
                ),
            )
            conn.commit()
    except sqlite3.Error:
        # Logging is best-effort; a DB hiccup should never fail the weather request.
        pass


def top_cities(limit: int = 20, since_hours: int | None = None) -> list[dict]:
    """Return the most-requested cities, most popular first."""
    query = (
        "SELECT city_requested, COUNT(*) as hits, MAX(ts) as last_seen "
        "FROM query_log "
    )
    params: list = []
    if since_hours is not None:
        query += "WHERE ts >= datetime('now', ?) "
        params.append(f"-{since_hours} hours")
    query += "GROUP BY LOWER(city_requested) ORDER BY hits DESC LIMIT ?"
    params.append(limit)

    with _connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def recent_queries(limit: int = 50) -> list[dict]:
    """Return the most recent raw queries (for debugging / inspection)."""
    with _connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM query_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
