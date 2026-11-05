import json
from types import SimpleNamespace

import pandas as pd
import pytest

from app import db
from app.ingest import map_columns, normalize, to_number
from app.verify import check_answer, extract_numbers


@pytest.fixture
def con(tmp_path):
    f = tmp_path / "t.csv"
    pd.DataFrame({
        "Bitim raqami": ["A1", "A2", "A3"],
        "Дата": ["01.10.2026", "02.10.2026", "02.10.2026"],
        "Tovar nomi": ["Sement M400", "Sement M400", "Bug'doy"],
        "Miqdor": ["100", "50", "20"],
        "Narx": ["850 000", "860 000", "3 200 000"],
        "Summa": ["85 000 000", "43 000 000", "64 000 000"],
        "Valyuta": ["UZS"] * 3,
    }).to_csv(f, index=False)
    c = db.connect(tmp_path / "t.db")
    db.load_file(c, f, exchange="UZEX")
    return c


def test_column_mapping_multilingual():
    m = map_columns(["Bitim raqami", "Дата", "Сумма сделки", "Xaridor", "random"])
    assert m == {"Bitim raqami": "deal_id", "Дата": "deal_date", "Сумма сделки": "amount", "Xaridor": "buyer"}


@pytest.mark.parametrize("raw,val", [("1 234 567,89", 1234567.89), ("1,234,567.89", 1234567.89),
                                     ("12,5", 12.5), ("850 000", 850000), ("-", None)])
def test_to_number(raw, val):
    assert to_number(raw) == val


def test_load_and_query(con):
    r = db.run_select(con, "SELECT SUM(amount) s, COUNT(*) n FROM deals WHERE deal_date='2026-10-02'")
    assert r["rows"][0] == [107000000.0, 2]
    # takroriy yuklash dublikat yaratmaydi
    assert db.describe(con)["total_rows"] == 3


@pytest.mark.parametrize("sql", ["DELETE FROM deals", "SELECT 1; DROP TABLE deals", "PRAGMA table_info(deals)",
                                 "WITH x AS (SELECT 1) INSERT INTO deals VALUES (1)"])
def test_sql_guard(con, sql):
    with pytest.raises(db.QueryError):
        db.run_select(con, sql)


def test_extract_numbers_scale_and_dates():
    nums = [v for _, v in extract_numbers("2026-10-02 kuni 107 mln so'm, 1 234,5 tonna")]
    assert 107e6 in nums and 1234.5 in nums and 2026 not in nums


def test_verifier_catches_invented_number():
    ev = [{"rows": [[107000000.0, 2]]}]
    assert check_answer("Jami 107 000 000 so'm, 2 ta bitim.", ev)["ok"]
    assert check_answer("Jami 107 mln so'm.", ev)["ok"]
    bad = check_answer("Jami 150 000 000 so'm.", ev)
    assert not bad["ok"] and bad["unsupported"] == ["150 000 000"]


# --- agent loop with a fake client (API kalitsiz) ---
def _msg(content, stop):
    return SimpleNamespace(content=content, stop_reason=stop)


def _text(t):
    return SimpleNamespace(type="text", text=t)


def _tool(i, name, inp):
    return SimpleNamespace(type="tool_use", id=i, name=name, input=inp)


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.messages = SimpleNamespace(create=lambda **kw: self.script.pop(0))


def test_agent_grounded_answer(con):
    from app.agent import BirjaAgent
    fake = FakeClient([
        _msg([_tool("t1", "run_sql", {"sql": "SELECT SUM(amount) FROM deals"})], "tool_use"),
        _msg([_text("Jami savdo: 192 000 000 so'm. Manba: t.csv")], "end_turn"),
    ])
    r = BirjaAgent(con, client=fake).ask("Jami savdo qancha?")
    assert r.verified and "192 000 000" in r.answer and r.queries


def test_agent_retries_then_warns(con):
    from app.agent import BirjaAgent
    fake = FakeClient([
        _msg([_text("Jami 999 999 so'm")], "end_turn"),
        _msg([_text("Jami 888 888 so'm")], "end_turn"),
    ])
    r = BirjaAgent(con, client=fake).ask("Jami?")
    assert not r.verified and "Ogohlantirish" in r.answer
