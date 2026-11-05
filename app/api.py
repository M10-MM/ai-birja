"""FastAPI server: birja sayti (bozor, aksiyalar, bitimlar), AI-agent va shaxsiy kabinet."""
from __future__ import annotations

import shutil
import threading
import time
from pathlib import Path

from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import auth, config, db, market
from .agent import BirjaAgent
from .offline import OfflineAgent

app = FastAPI(title="AI Birja — birja bitimlari AI-agenti", version="0.2.0")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

_local = threading.local()  # SQLite ulanishi har bir oqim (thread) uchun alohida


def ro():
    if getattr(_local, "ro", None) is None:
        _local.ro = db.connect(readonly=True)
    return _local.ro


def users():
    if getattr(_local, "users", None) is None:
        _local.users = auth.connect()
    return _local.users


def _token(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def _uid(authorization: str | None, required: bool = True) -> int | None:
    uid = auth.user_id(users(), _token(authorization))
    if required and not uid:
        raise HTTPException(401, "unauthorized")
    return uid


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


# ---------- ma'lumotlar qamrovi ----------
@app.get("/api/data")
def data_info():
    return db.describe(ro())


# ---------- bozor ----------
@app.get("/api/market/ticker")
def ticker():
    return market.commodity_ticker(ro())


@app.get("/api/market/overview")
def overview():
    return market.overview(ro())


@app.get("/api/deals")
def deals(q: str = "", date_from: str = "", date_to: str = "", page: int = 1, size: int = 50,
          sort: str = "deal_date", order: str = "desc", instrument: str = "", category: str = "",
          region: str = "", market_: str = Query("", alias="market"), seller: str = "", buyer: str = ""):
    return market.deals(ro(), q, date_from, date_to, page, size, sort, order, instrument=instrument,
                        category=category, region=region, market=market_, seller=seller, buyer=buyer)


@app.get("/api/deals/facets")
def facets():
    return market.deal_facets(ro())


@app.get("/api/commodity/{code}")
def commodity(code: str):
    r = market.commodity(ro(), code)
    if not r:
        raise HTTPException(404, "not found")
    return r


@app.get("/api/stocks")
def stocks():
    return market.stocks(ro())


@app.get("/api/stocks/liquidity")
def liquidity():
    return market.liquidity(ro())


@app.get("/api/stocks/trades")
def stock_trades(limit: int = 10, ticker: str = ""):
    return market.stock_trades(ro(), limit, ticker)


@app.get("/api/stocks/listings")
def listings():
    return market.listings(ro())


@app.get("/api/stocks/{ticker}")
def stock(ticker: str):
    r = market.stock(ro(), ticker.upper())
    if not r:
        raise HTTPException(404, "not found")
    return r


@app.get("/api/usd")
def usd():
    return market.usd_rates(ro())


@app.get("/api/participants")
def participants():
    return market.table_rows(ro(), "participants")


@app.get("/api/brokers")
def brokers():
    return market.table_rows(ro(), "brokers")


# ---------- AI-agent ----------
class Ask(BaseModel):
    question: str
    history: list[dict] = []  # [{"q": "...", "a": "..."}] — oldingi savol-javoblar (kontekst uchun)


@app.post("/api/ask")
def ask(body: Ask, authorization: str | None = Header(None)):
    if not body.question.strip():
        raise HTTPException(400, "empty question")
    hist = []
    for h in body.history[-3:]:
        if h.get("q") and h.get("a"):
            hist += [{"role": "user", "content": h["q"]}, {"role": "assistant", "content": h["a"]}]
    t0 = time.time()
    con = db.connect(readonly=True)
    engine, note = "offline", None
    r = None
    if config.ANTHROPIC_API_KEY:
        try:
            r = BirjaAgent(con).ask(body.question, history=hist)
            engine = "claude"
        except Exception as e:  # API xatosi -> oflayn rejim
            note = f"Claude API: {type(e).__name__}"
    if r is None:
        r = OfflineAgent(con).ask(body.question)
    evidence = [
        {"columns": t["columns"], "rows": t["rows"][:15], "row_count": t["row_count"], "truncated": t["truncated"]}
        for t in r.tool_results if isinstance(t, dict) and "columns" in t
    ]
    uid = _uid(authorization, required=False)
    if uid:
        auth.add_history(users(), uid, body.question, r.answer, r.verified, r.queries)
    return {"answer": r.answer, "verified": r.verified, "unsupported": r.unsupported,
            "queries": r.queries, "evidence": evidence, "seconds": round(time.time() - t0, 1),
            "engine": engine, "note": note}


# ---------- kabinet ----------
class Register(BaseModel):
    login: str
    password: str
    name: str = ""
    role: str = "investor"


class Login(BaseModel):
    login: str
    password: str
    role: str | None = None


class Watch(BaseModel):
    kind: str  # stock | commodity
    code: str


@app.post("/api/auth/register")
def register(b: Register):
    try:
        return auth.register(users(), b.login, b.password, b.name, b.role)
    except auth.AuthError as e:
        raise HTTPException(400, str(e))


@app.post("/api/auth/login")
def login(b: Login):
    try:
        return auth.login(users(), b.login, b.password, b.role)
    except auth.AuthError as e:
        raise HTTPException(401, str(e))


@app.post("/api/auth/logout")
def logout(authorization: str | None = Header(None)):
    if t := _token(authorization):
        auth.logout(users(), t)
    return {"ok": True}


@app.get("/api/me")
def me(authorization: str | None = Header(None)):
    uid = _uid(authorization)
    return {"user": auth.me(users(), uid), "watchlist": auth.watchlist(users(), uid)}


@app.post("/api/me/watch")
def watch(b: Watch, authorization: str | None = Header(None)):
    return auth.toggle_watch(users(), _uid(authorization), b.kind, b.code)


@app.get("/api/me/history")
def my_history(authorization: str | None = Header(None)):
    return auth.history(users(), _uid(authorization))


# ---------- fayl yuklash ----------
@app.post("/api/upload")
async def upload(file: UploadFile = File(...), exchange: str | None = None,
                 authorization: str | None = Header(None)):
    _uid(authorization)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls", ".json", ".html", ".htm"}:
        raise HTTPException(400, "Format: CSV, XLSX, JSON yoki HTML")
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = config.RAW_DIR / Path(file.filename).name
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        return db.load_file(db.connect(), dest, exchange=exchange)
    except Exception as e:
        raise HTTPException(400, f"Faylni o'qib bo'lmadi: {e}")
