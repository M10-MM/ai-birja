"""Sayt API: bozor, aksiyalar, kabinet va /api/ask (soxta model bilan, API kalitsiz)."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app import api, auth, config, db, market


@pytest.fixture
def client(tmp_path, monkeypatch, con):
    dbfile = tmp_path / "t.db"
    monkeypatch.setattr(config, "DB_PATH", dbfile)
    monkeypatch.setattr(auth, "USERS_DB", tmp_path / "u.db")
    api._local.__dict__.clear()
    return TestClient(api.app)


@pytest.fixture
def con(tmp_path):
    import pandas as pd
    f = tmp_path / "d.csv"
    pd.DataFrame({
        "Bitim raqami": ["A1", "A2", "A3"], "Sana": ["01.10.2026", "02.10.2026", "02.10.2026"],
        "Kod": ["CEM", "CEM", "WHT"], "Tovar nomi": ["Sement M400", "Sement M400", "Bug'doy"],
        "Guruh": ["Qurilish", "Qurilish", "Don"], "Miqdor": ["100", "50", "20"],
        "Narx": ["850 000", "860 000", "3 200 000"], "Summa": ["85 000 000", "43 000 000", "64 000 000"],
        "Valyuta": ["UZS"] * 3,
    }).to_csv(f, index=False)
    c = db.connect(tmp_path / "t.db")
    db.load_file(c, f, exchange="UZEX")
    return c


def test_market_endpoints(client):
    t = client.get("/api/market/ticker").json()
    cem = next(x for x in t if x["code"] == "CEM")
    assert cem["price"] == 860000 and cem["prev"] == 850000 and cem["change_pct"] == pytest.approx(1.18)
    d = client.get("/api/deals?instrument=CEM").json()
    assert d["total"] == 2 and d["sum_amount"] == 128000000
    assert client.get("/api/stocks").json() == []  # aksiyalar jadvali yo'q — bo'sh, xatosiz


def test_auth_flow(client):
    assert client.post("/api/auth/register", json={"login": "ab", "password": "123"}).status_code == 400
    r = client.post("/api/auth/register", json={"login": "Ali", "password": "secret1", "name": "Ali V"}).json()
    h = {"Authorization": "Bearer " + r["token"]}
    assert client.post("/api/auth/register", json={"login": "ali", "password": "secret1"}).status_code == 400
    assert client.post("/api/auth/login", json={"login": "ali", "password": "wrong"}).status_code == 401
    assert client.post("/api/auth/login", json={"login": "ali", "password": "secret1"}).status_code == 200
    assert client.post("/api/me/watch", json={"kind": "stock", "code": "IPTB"}, headers=h).json() == [{"kind": "stock", "code": "IPTB"}]
    assert client.get("/api/me").status_code == 401


def test_ask_returns_evidence_and_history(client, monkeypatch):
    calls = iter([
        SimpleNamespace(stop_reason="tool_use", content=[SimpleNamespace(
            type="tool_use", id="t1", name="run_sql", input={"sql": "SELECT SUM(amount) s FROM deals WHERE instrument='CEM'"})]),
        SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="Sement: 128 000 000 so'm.")]),
    ])
    fake = SimpleNamespace(messages=SimpleNamespace(create=lambda **k: next(calls)))
    orig = api.BirjaAgent
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(api, "BirjaAgent", lambda con: orig(con, client=fake))
    tok = client.post("/api/auth/register", json={"login": "bob", "password": "secret1"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    r = client.post("/api/ask", json={"question": "Sement summasi?"}, headers=h).json()
    assert r["verified"] and r["evidence"][0]["rows"] == [[128000000.0]]
    assert client.get("/api/me/history", headers=h).json()[0]["question"] == "Sement summasi?"


# --- oflayn agent (LLM kalitisiz) ---
from app.offline import OfflineAgent


def test_offline_sum_is_exact_and_verified(con):
    r = OfflineAgent(con).ask("Сколько сделок по цементу в октябре 2026 и на какую сумму?")
    assert "2 сделок" in r.answer and "128 000 000" in r.answer and r.verified


def test_offline_top_commodity_uz(con):
    r = OfflineAgent(con).ask("2026-yil oktabr oyida eng ko'p summa qaysi tovarda?")
    assert r.answer.splitlines()[1].startswith("1. Sement M400") and r.verified


def test_offline_says_no_data(con):
    assert "нет сделок по товару «золото»" in OfflineAgent(con).ask("Сколько сделок по золоту в 2023?").answer
    assert "no deals in 2030" in OfflineAgent(con).ask("How many cement deals in 2030?").answer


def test_offline_refuses_unclear(con):
    r = OfflineAgent(con).ask("Привет, как дела?")
    assert "не отвечаю наугад" in r.answer and not r.queries[1:]


def test_ask_without_key_uses_offline(client, monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    d = client.post("/api/ask", json={"question": "Cement turnover in October 2026"}).json()
    assert d["engine"] == "offline" and d["verified"] and "128 000 000" in d["answer"]


def test_offline_real_quotes(tmp_path):
    from pathlib import Path
    c = db.connect(tmp_path / "q.db")
    market.load_reference(c, Path(__file__).parent.parent / "data" / "real")
    r = OfflineAgent(c).ask("Какая цена акций TRSBP?")
    assert "155 500" in r.answer and "130 000" in r.answer and r.verified
    r = OfflineAgent(c).ask("What is the current price of gold?")
    assert "1 613 453.93" in r.answer and r.verified
    assert len(market.stocks(c)) == 71 and len(market.commodity_ticker(c)) == 27
    assert market.liquidity(c)["high"] == 54
