"""Sayt uchun bozor ma'lumotlari: tovar tikeri, bitimlar reyestri, aksiyalar, likvidlik.

Barcha qiymatlar to'g'ridan-to'g'ri bazadan hisoblanadi — hech narsa qo'lda yozilmaydi.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

REF_FILES = {  # fayl nomi -> jadval
    "stock_trades.csv": "stock_trades",
    "listings.csv": "listings",
    "participants.csv": "participants",
    "brokers.csv": "brokers",
    "usd_rate.csv": "usd_rate",
    "uzex_quotes.csv": "uzex_quotes",
    "uzse_quotes.csv": "uzse_quotes",
    "liquidity.csv": "liquidity",
}


def load_reference(con: sqlite3.Connection, folder: Path) -> list[dict]:
    out = []
    for fname, table in REF_FILES.items():
        f = Path(folder) / fname
        if not f.exists():
            continue
        df = pd.read_csv(f)
        df.to_sql(table, con, if_exists="replace", index=False)
        out.append({"file": fname, "table": table, "rows": len(df)})
    if any(o["table"] == "stock_trades" for o in out):
        con.execute("CREATE INDEX IF NOT EXISTS ix_st_ticker ON stock_trades(ticker, trade_time)")
        con.execute("CREATE INDEX IF NOT EXISTS ix_st_time ON stock_trades(trade_time)")
    con.execute("CREATE INDEX IF NOT EXISTS ix_deals_code_date ON deals(instrument, deal_date)")
    con.commit()
    return out


def _has(con, table: str) -> bool:
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone() is not None


def _rows(cur) -> list[dict]:
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


# ---------------- Tovar birjasi ----------------
def _deals_ticker(con) -> list[dict]:
    """Har bir tovar: oxirgi savdo kunidagi o'rtacha tortilgan narx va oldingi kunga nisbatan o'zgarish."""
    sql = """
    WITH daily AS (
      SELECT instrument, instrument_name, deal_date, SUM(amount)/SUM(quantity) vwap, SUM(amount) turnover
      FROM deals WHERE quantity > 0 GROUP BY instrument, deal_date
    ), ranked AS (
      SELECT *, ROW_NUMBER() OVER (PARTITION BY instrument ORDER BY deal_date DESC) rn FROM daily
    )
    SELECT a.instrument code, a.instrument_name name, a.deal_date date, ROUND(a.vwap,2) price,
           ROUND(b.vwap,2) prev, ROUND(a.turnover,2) turnover
    FROM ranked a LEFT JOIN ranked b ON a.instrument=b.instrument AND b.rn=2
    WHERE a.rn=1 ORDER BY a.turnover DESC
    """
    out = _rows(con.execute(sql))
    for r in out:
        r["change"] = round(r["price"] - r["prev"], 2) if r["prev"] else 0.0
        r["change_pct"] = round(r["change"] / r["prev"] * 100, 2) if r["prev"] else 0.0
    return out


def overview(con) -> dict:
    last = con.execute("SELECT MAX(deal_date) FROM deals").fetchone()[0]
    day = con.execute(
        "SELECT COUNT(*) n, ROUND(SUM(amount),2) s FROM deals WHERE deal_date=?", (last,)).fetchone()
    month = con.execute(
        "SELECT COUNT(*) n, ROUND(SUM(amount),2) s FROM deals WHERE substr(deal_date,1,7)=substr(?,1,7)", (last,)).fetchone()
    tot = con.execute("SELECT COUNT(*), MIN(deal_date), MAX(deal_date) FROM deals").fetchone()
    res = {
        "last_date": last, "day_deals": day[0], "day_turnover": day[1],
        "month_deals": month[0], "month_turnover": month[1],
        "total_deals": tot[0], "date_from": tot[1], "date_to": tot[2],
        "categories": _rows(con.execute(
            "SELECT category, COUNT(*) deals, ROUND(SUM(amount),2) turnover FROM deals "
            "WHERE substr(deal_date,1,7)=substr(?,1,7) GROUP BY category ORDER BY turnover DESC", (last,))),
        "monthly": _rows(con.execute(
            "SELECT substr(deal_date,1,7) month, COUNT(*) deals, ROUND(SUM(amount),2) turnover "
            "FROM deals GROUP BY month ORDER BY month")),
    }
    if _has(con, "usd_rate"):
        r = con.execute("SELECT date, usd_uzs FROM usd_rate ORDER BY date DESC LIMIT 2").fetchall()
        if r:
            res["usd"] = {"date": r[0][0], "rate": r[0][1], "prev": r[1][1] if len(r) > 1 else None}
    return res


DEAL_FILTERS = {"instrument", "category", "region", "market", "seller", "buyer"}


def deals(con, q: str = "", date_from: str = "", date_to: str = "", page: int = 1, size: int = 50,
          sort: str = "deal_date", order: str = "desc", **filters) -> dict:
    where, params = ["1=1"], []
    if q:
        where.append("(LOWER(instrument_name) LIKE ? OR LOWER(deal_id) LIKE ? OR LOWER(buyer) LIKE ? OR LOWER(seller) LIKE ?)")
        params += [f"%{q.lower()}%"] * 4
    if date_from:
        where.append("deal_date >= ?"); params.append(date_from)
    if date_to:
        where.append("deal_date <= ?"); params.append(date_to)
    for k, v in filters.items():
        if k in DEAL_FILTERS and v:
            where.append(f"{k} = ?"); params.append(v)
    w = " AND ".join(where)
    sort = sort if sort in {"deal_date", "amount", "price", "quantity", "instrument_name"} else "deal_date"
    order = "ASC" if order.lower() == "asc" else "DESC"
    total, s = con.execute(f"SELECT COUNT(*), ROUND(SUM(amount),2) FROM deals WHERE {w}", params).fetchone()
    size = max(1, min(size, 200))
    rows = _rows(con.execute(
        f"SELECT deal_id, deal_date, market, instrument, instrument_name, category, quantity, unit, price, amount, "
        f"currency, seller, buyer, region, seller_broker, buyer_broker, source_file, source_row FROM deals WHERE {w} "
        f"ORDER BY {sort} {order}, deal_id {order} LIMIT ? OFFSET ?", params + [size, (max(page, 1) - 1) * size]))
    return {"total": total, "sum_amount": s, "page": page, "size": size, "rows": rows}


def deal_facets(con) -> dict:
    f = lambda c: [r[0] for r in con.execute(f"SELECT DISTINCT {c} FROM deals WHERE {c} IS NOT NULL ORDER BY 1")]
    return {"category": f("category"), "region": f("region"), "market": f("market"),
            "instrument": _rows(con.execute("SELECT DISTINCT instrument code, instrument_name name FROM deals ORDER BY name"))}


def _deals_commodity(con, code: str) -> dict:
    info = con.execute(
        "SELECT instrument, instrument_name, category, unit, COUNT(*), ROUND(SUM(amount),2), SUM(quantity), "
        "MIN(deal_date), MAX(deal_date) FROM deals WHERE instrument=?", (code,)).fetchone()
    if not info or not info[0]:
        return {}
    series = _rows(con.execute(
        "SELECT substr(deal_date,1,7) month, ROUND(SUM(amount)/SUM(quantity),2) vwap, ROUND(MIN(price),2) low, "
        "ROUND(MAX(price),2) high, SUM(quantity) qty, ROUND(SUM(amount),2) turnover, COUNT(*) deals "
        "FROM deals WHERE instrument=? GROUP BY month ORDER BY month", (code,)))
    top_buyers = _rows(con.execute(
        "SELECT buyer, COUNT(*) deals, ROUND(SUM(amount),2) turnover FROM deals WHERE instrument=? "
        "GROUP BY buyer ORDER BY turnover DESC LIMIT 10", (code,)))
    return {"code": info[0], "name": info[1], "category": info[2], "unit": info[3], "deals": info[4],
            "turnover": info[5], "quantity": info[6], "date_from": info[7], "date_to": info[8],
            "series": series, "top_buyers": top_buyers}


# ---------------- Fond birjasi (aksiyalar) ----------------
def _liq_level(months: int) -> str:
    return "high" if months >= 10 else "mid" if months >= 6 else "low"


def _demo_stocks(con) -> list[dict]:
    if not _has(con, "stock_trades"):
        return []
    last = con.execute("SELECT MAX(trade_time) FROM stock_trades").fetchone()[0]
    sql = """
    WITH d AS (
      SELECT ticker, substr(trade_time,1,10) day, SUM(volume) vol, SUM(quantity) qty, COUNT(*) n,
             MAX(trade_time) lt
      FROM stock_trades GROUP BY ticker, day
    ), lastp AS (
      SELECT t.ticker, t.price, d.day, ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY d.day DESC) rn
      FROM d JOIN stock_trades t ON t.ticker=d.ticker AND t.trade_time=d.lt
    ), m AS (
      SELECT ticker, COUNT(DISTINCT substr(trade_time,1,7)) months FROM stock_trades
      WHERE trade_time >= date(?, 'start of month', '-11 months') GROUP BY ticker
    )
    SELECT l.ticker, l.isin, l.issuer, l.sec_type, l.currency, l.nominal, l.shares, l.listed_date,
           a.price, a.day last_day, b.price prev,
           (SELECT ROUND(SUM(vol),2) FROM d WHERE d.ticker=l.ticker AND d.day=a.day) day_volume,
           (SELECT ROUND(SUM(vol),2) FROM d WHERE d.ticker=l.ticker AND d.day > date(?, '-30 days')) vol_30d,
           COALESCE(m.months,0) months
    FROM listings l
    LEFT JOIN lastp a ON a.ticker=l.ticker AND a.rn=1
    LEFT JOIN lastp b ON b.ticker=l.ticker AND b.rn=2
    LEFT JOIN m ON m.ticker=l.ticker
    ORDER BY vol_30d DESC NULLS LAST
    """
    out = _rows(con.execute(sql, (last, last)))
    for r in out:
        r["change"] = round(r["price"] - r["prev"], 4) if r["price"] and r["prev"] else 0.0
        r["change_pct"] = round(r["change"] / r["prev"] * 100, 2) if r["prev"] else 0.0
        r["liquidity"] = _liq_level(r["months"])
        r["cap"] = round(r["price"] * r["shares"], 2) if r["price"] else None
    return out


def _demo_liquidity(con) -> dict:
    st = _demo_stocks(con)
    last = con.execute("SELECT MAX(trade_time) FROM stock_trades").fetchone()[0] if st else None
    lv = {k: [s for s in st if s["liquidity"] == k] for k in ("high", "mid", "low")}
    top = sorted(lv["high"], key=lambda s: (-s["months"], s["ticker"]))[:10]
    return {"as_of": last[:7] if last else None, "total": len(st),
            "high": len(lv["high"]), "mid": len(lv["mid"]), "low": len(lv["low"]),
            "top": [{"ticker": s["ticker"], "months": s["months"]} for s in top]}


def _demo_stock(con, ticker: str) -> dict:
    s = next((x for x in _demo_stocks(con) if x["ticker"] == ticker), None)
    if not s:
        return {}
    s["series"] = _rows(con.execute(
        """SELECT day, close, vol FROM (
             SELECT substr(trade_time,1,10) day, price close, trade_time,
                    SUM(volume) OVER (PARTITION BY substr(trade_time,1,10)) vol,
                    ROW_NUMBER() OVER (PARTITION BY substr(trade_time,1,10) ORDER BY trade_time DESC) rn
             FROM stock_trades WHERE ticker=?) WHERE rn=1 ORDER BY day""", (ticker,)))
    s["trades"] = _rows(con.execute(
        "SELECT trade_time, price, quantity, volume, currency FROM stock_trades WHERE ticker=? "
        "ORDER BY trade_time DESC LIMIT 30", (ticker,)))
    return s


def stock_trades(con, limit: int = 10, ticker: str = "") -> list[dict]:
    if not _has(con, "stock_trades"):
        return []
    w, p = ("WHERE ticker=?", [ticker]) if ticker else ("", [])
    return _rows(con.execute(
        f"SELECT trade_time, ticker, isin, issuer, sec_type, market, board, price, quantity, volume, currency "
        f"FROM stock_trades {w} ORDER BY trade_time DESC LIMIT ?", p + [min(limit, 200)]))


def listings(con) -> list[dict]:
    if not _has(con, "listings"):
        return []
    return _rows(con.execute(
        "SELECT ticker, listed_date, currency, nominal, shares, issuer FROM listings ORDER BY listed_date DESC"))


def table_rows(con, table: str, limit: int = 500) -> list[dict]:
    if table not in {"participants", "brokers"} or not _has(con, table):
        return []
    return _rows(con.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)))


def usd_rates(con) -> list[dict]:
    if not _has(con, "usd_rate"):
        return []
    return _rows(con.execute("SELECT date, usd_uzs FROM usd_rate ORDER BY date"))



# ---------------- Haqiqiy kotirovkalar (data/real) ustuvor ----------------
# uzex_quotes / uzse_quotes / liquidity jadvallari bo'lsa — sayt ulardan foydalanadi, bo'lmasa DEMO hisob-kitobdan.
import re as _re


def _slug(name: str) -> str:
    from .offline import norm
    return "Q-" + _re.sub(r"[^a-z0-9]+", "-", norm(name)).strip("-")[:48]


def commodity_ticker(con) -> list[dict]:
    if not _has(con, "uzex_quotes"):
        return _deals_ticker(con)
    out = _rows(con.execute(
        "SELECT name, category, quote_date date, price, change_abs change, change_pct, currency, source "
        "FROM uzex_quotes ORDER BY rowid"))
    for r in out:
        r["code"] = _slug(r["name"])
        r["prev"] = round(r["price"] - r["change"], 2)
        r["turnover"] = None
        r["real"] = True
    return out


def commodity(con, code: str) -> dict:
    if code.startswith("Q-") and _has(con, "uzex_quotes"):
        q = next((x for x in commodity_ticker(con) if x["code"] == code), None)
        if not q:
            return {}
        first = q["name"].split()[0]
        n = con.execute("SELECT COUNT(*) FROM deals WHERE instrument_name LIKE ?", (first + "%",)).fetchone()[0]
        return {"code": code, "name": q["name"], "category": q["category"], "quote": q,
                "registry_query": first if n else None, "registry_deals": n}
    return _deals_commodity(con, code)


def _sec_type(issuer: str) -> str:
    return "pref" if "прив" in (issuer or "") else "common"


def stocks(con) -> list[dict]:
    if not _has(con, "uzse_quotes"):
        return _demo_stocks(con)
    liq = {t["ticker"]: t["months"] for t in liquidity(con).get("top", [])}
    trades = {}
    if _has(con, "stock_trades"):
        trades = {r[0]: (r[1], r[2], r[3]) for r in con.execute(
            "SELECT ticker, MAX(isin), COUNT(*), ROUND(SUM(volume),2) FROM stock_trades GROUP BY ticker")}
    out = _rows(con.execute(
        "SELECT ticker, issuer, close_price close, last_price price, change_abs change, currency, quote_date last_day, source "
        "FROM uzse_quotes ORDER BY rowid"))
    for r in out:
        r["sec_type"] = _sec_type(r["issuer"])
        r["prev"] = round(r["price"] - r["change"], 4)
        r["change_pct"] = round(r["change"] / r["prev"] * 100, 2) if r["prev"] else 0.0
        t = trades.get(r["ticker"])
        r["isin"] = t[0] if t else ""
        r["day_trades"], r["day_volume"] = (t[1], t[2]) if t else (0, None)
        r["months"] = liq.get(r["ticker"])
        r["liquidity"] = None if r["months"] is None else ("high" if r["months"] >= 10 else "mid" if r["months"] >= 6 else "low")
        r["real"] = True
    return out


def liquidity(con) -> dict:
    if not _has(con, "liquidity"):
        return _demo_liquidity(con)
    r = con.execute("SELECT as_of, total, high, mid, low, top FROM liquidity LIMIT 1").fetchone()
    top = [{"ticker": x.split(":")[0], "months": int(x.split(":")[1])} for x in (r[5] or "").split(";") if ":" in x]
    return {"as_of": r[0], "total": r[1], "high": r[2], "mid": r[3], "low": r[4], "top": top, "real": True}


def stock(con, ticker: str) -> dict:
    if not _has(con, "uzse_quotes"):
        return _demo_stock(con, ticker)
    s = next((x for x in stocks(con) if x["ticker"] == ticker), None)
    if not s:
        return {}
    s["series"] = []
    s["trades"] = _rows(con.execute(
        "SELECT trade_time, price, quantity, volume, currency FROM stock_trades WHERE ticker=? "
        "ORDER BY trade_time DESC LIMIT 50", (ticker,))) if _has(con, "stock_trades") else []
    s["series"] = [{"day": t["trade_time"], "close": t["price"]} for t in reversed(s["trades"])]
    return s
