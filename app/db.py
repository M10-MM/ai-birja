"""SQLite ombori va xavfsiz (faqat o'qish) SQL bajaruvchi."""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

from . import config
from .ingest import CANONICAL, normalize, read_any

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS deals (
    {", ".join(f"{c} {'REAL' if c in ('quantity','price','amount') else 'TEXT'}" for c in CANONICAL)},
    source_file TEXT, source_row INTEGER, row_hash TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS ix_deals_date ON deals(deal_date);
CREATE INDEX IF NOT EXISTS ix_deals_instr ON deals(instrument);
CREATE TABLE IF NOT EXISTS sources (
    source_file TEXT PRIMARY KEY, exchange TEXT, url TEXT, loaded_at TEXT, rows INTEGER
);
"""


def connect(path: Path | None = None, readonly: bool = False) -> sqlite3.Connection:
    path = Path(path or config.DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    if readonly:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    else:
        con = sqlite3.connect(path, check_same_thread=False)
        con.executescript(SCHEMA)
    con.row_factory = sqlite3.Row
    return con


def load_file(con: sqlite3.Connection, file: Path, exchange: str | None = None, url: str | None = None) -> dict:
    df = normalize(read_any(file), source_file=file.name, exchange=exchange)
    before = con.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
    df.to_sql("_staging", con, if_exists="replace", index=False)
    con.execute("INSERT OR IGNORE INTO deals SELECT * FROM _staging")
    con.execute("DROP TABLE _staging")
    added = con.execute("SELECT COUNT(*) FROM deals").fetchone()[0] - before
    con.execute(
        "INSERT OR REPLACE INTO sources VALUES (?,?,?,datetime('now'),?)",
        (file.name, exchange, url, int(len(df))),
    )
    con.commit()
    return {"file": file.name, "rows": len(df), "added": added, "unmapped_columns": df.attrs.get("unmapped", [])}


# ---------- Agent uchun xavfsiz so'rovlar ----------
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex|trigger)\b",
    re.I,
)


class QueryError(ValueError):
    pass


def check_sql(sql: str) -> str:
    s = sql.strip().rstrip(";").strip()
    if ";" in s:
        raise QueryError("Faqat bitta SQL so'rov ruxsat etiladi.")
    if not re.match(r"^(select|with)\b", s, re.I):
        raise QueryError("Faqat SELECT so'rovlari ruxsat etiladi.")
    if _FORBIDDEN.search(s):
        raise QueryError("So'rovda taqiqlangan kalit so'z bor.")
    return s


def run_select(con: sqlite3.Connection, sql: str, max_rows: int | None = None) -> dict:
    s = check_sql(sql)
    max_rows = max_rows or config.MAX_ROWS
    cur = con.execute(s)
    cols = [d[0] for d in cur.description or []]
    rows = cur.fetchmany(max_rows + 1)
    truncated = len(rows) > max_rows
    return {
        "columns": cols,
        "rows": [list(r) for r in rows[:max_rows]],
        "row_count": min(len(rows), max_rows),
        "truncated": truncated,
    }


def describe(con: sqlite3.Connection) -> dict:
    """Agentga beriladigan sxema + ma'lumotlar qamrovi (qaysi sanalar, birjalar bor)."""
    total = con.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
    cov = con.execute("SELECT MIN(deal_date), MAX(deal_date) FROM deals").fetchone()
    by_ex = con.execute(
        "SELECT exchange, COUNT(*) n FROM deals GROUP BY exchange ORDER BY n DESC"
    ).fetchall()
    cur = con.execute(
        "SELECT currency, COUNT(*) n FROM deals GROUP BY currency ORDER BY n DESC"
    ).fetchall()
    sources = con.execute("SELECT source_file, exchange, url, loaded_at, rows FROM sources").fetchall()
    return {
        "table": "deals",
        "columns": {**CANONICAL, "source_file": "Manba fayl", "source_row": "Fayldagi qator raqami"},
        "total_rows": total,
        "date_range": [cov[0], cov[1]],
        "exchanges": {r[0] or "?": r[1] for r in by_ex},
        "currencies": {r[0] or "?": r[1] for r in cur},
        "sources": [dict(r) for r in sources],
        "other_tables": other_tables(con),
    }


OTHER_TABLES = {
    "stock_trades": "Fond birjasi (aksiyalar) bitimlari: trade_time 'YYYY-MM-DD HH:MM', ticker, isin, issuer, sec_type (common/pref), price, quantity, volume, currency",
    "listings": "Kotirovka varag'idagi qimmatli qog'ozlar: ticker, isin, issuer, sec_type, currency, nominal, shares, listed_date",
    "participants": "Savdo ishtirokchilari: name, role (seller/buyer), region, inn",
    "brokers": "Brokerlar: code, name, license",
    "usd_rate": "Dollar kursi: date (YYYY-MM-DD), usd_uzs (1 USD necha so'm)",
    "uzex_quotes": "UZEX tovar kotirovkalari (bir kunlik): quote_date, name, category, price (o'rtacha narx UZS), change_abs, change_pct, source",
    "uzse_quotes": "UZSE aksiyalar kotirovkasi: quote_date, ticker, issuer, close_price (yopilish), last_price (oxirgi bitim), change_abs, source",
    "liquidity": "Aksiyalar likvidligi (qisqa): as_of, total, high, mid, low, top ('TIKER:oylar;...')",
}


def other_tables(con: sqlite3.Connection) -> dict:
    out = {}
    for t, desc in OTHER_TABLES.items():
        if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
            cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
            n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            out[t] = {"description": desc, "columns": cols, "rows": n}
    return out


def distinct_values(con: sqlite3.Connection, column: str, like: str | None = None, limit: int = 50) -> list:
    if column not in CANONICAL:
        raise QueryError(f"Noma'lum ustun: {column}")
    q = f"SELECT {column}, COUNT(*) n FROM deals WHERE {column} IS NOT NULL"
    params: list = []
    if like:
        q += f" AND LOWER({column}) LIKE ?"
        params.append(f"%{like.lower()}%")
    q += f" GROUP BY {column} ORDER BY n DESC LIMIT ?"
    params.append(limit)
    return [[r[0], r[1]] for r in con.execute(q, params).fetchall()]


def to_frame(result: dict) -> pd.DataFrame:
    return pd.DataFrame(result["rows"], columns=result["columns"])
