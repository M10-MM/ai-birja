"""Tanlov reyestri (uzex_spot_data) importi: shartnoma bilan bog'lash, USD -> UZS, kg -> tonna, bekor qilinganlar."""
import pytest

from app import db, market, uzex
from app.offline import OfflineAgent

DEAL_COLS = ("Номер сделки,Дата сделки,Время сделки,Тип торгов,Количество,Сумма сделки,Стартовая цена,Номер контракта,"
             "Наименование товара,Лот,Единица измерения,Регион,Тип контракта,Форма контракта,Состояние сделки,"
             "ИНН продавца,ИНН покупателя,Брокер продавца,Брокер покупателя,Дата оплаты,Дата поставки,Поставлено")
CONTRACT_COLS = ("Номер контракта,Наименование продукта,Марка товара,Размер товара,Сорт товара,Тип товара,Класс товара,"
                 "Код ТН ВЭД,Группа товара,Категория товара,Отрасль промышленности,Единица измерения,Лот,Валюта,"
                 "Базисная цена,Сумма залога,Базис поставки,Регион,Адрес склада,Тип торгов,Тип контракта,"
                 "Форма контракта,Срок оплаты,Срок поставки,Упаковка,ИНН продавца,Дата регистрации,Действует до")


def _contract(no, name, hs, cat, unit, lot, cur):
    return (f"{no},{name},,,,,,{hs},Высоколиквидные товары,{cat},Отрасль,{unit},{lot},{cur},100,10 %,EXW,"
            f"Ташкент,\"адрес\",Английский аукцион,Внутренний,Спот,5,10,навалом,900000001,03.01.2022,31.12.2026")


@pytest.fixture
def data(tmp_path):
    d = tmp_path / "uzex_spot_data"
    d.mkdir()
    (d / "contracts.csv").write_text("\n".join([
        CONTRACT_COLS,
        _contract(1, "Мука пшеничная", "110100", "Продовольственные товары", "килограмм", 1, "Узбекский сум"),
        _contract(2, "Катод медный", "740311", "Металлопродукция", "тонна", 1, "Доллар США"),
        _contract(3, "Топливо дизельное", "271019", "Нефтепродукты", "килограмм", 1, "Узбекский сум"),
    ]), encoding="utf-8")
    (d / "deals_2025.csv").write_text("\n".join([
        DEAL_COLS,
        "10,02.01.2025,10:00:00,Английский аукцион,1000,5 000 000,4 900,1,МУКА ПШЕНИЧНАЯ 1 сорт,1,килограмм,"
        "Toshkent shahri,Внутренний,Спот,Исполнен,900000001,900000002,BK001,BK002,05.01.2025,10.01.2025,1000",
        "11,02.01.2025,11:00:00,Английский аукцион,2,20 000.5,9 000,2,Катод медный М0к,1,тонна,"
        "Navoiy viloyati,Экспортный,Спот,Исполнен,900000001,900000002,BK001,BK002,05.01.2025,10.01.2025,2",
        "12,03.01.2025,12:00:00,Обратный аукцион,5000,60 000 000,12 500,3,Топливо дизельное,1,килограмм,"
        "Buxoro viloyati,Внутренний,Спот,Аннулирован(Не оплачен),900000001,900000002,BK002,BK001,,,",
    ]), encoding="utf-8")
    (d / "participants.csv").write_text(
        "ИНН,Наименование,Регион,Вид деятельности,Роль,Плательщик НДС\n"
        '900000001,"""Alfa"" MChJ",Toshkent shahri,Производитель,Продавец,Да\n'
        "900000002,BETA MCHJ,Navoiy viloyati,Торговая компания,Покупатель,Нет\n", encoding="utf-8")
    (d / "brokers.csv").write_text(
        "Код брокера,Наименование,ИНН,Регион\nBK001,ONE BROKER MCHJ,911111111,Toshkent shahri\n"
        "BK002,TWO BROKER MCHJ,922222222,Buxoro viloyati\n", encoding="utf-8")
    (d / "usd_rates.csv").write_text("Дата,Курс\n01.01.2025,12900\n02.01.2025,13000\n03.01.2025,13010\n", encoding="utf-8")
    return d


def test_load_registry(tmp_path, data):
    con = db.connect(tmp_path / "t.db")
    res = uzex.load(con, data)
    assert res["deals"] == 3 and res["participants"] == 2 and res["brokers"] == 2
    rows = {r["deal_id"]: dict(r) for r in con.execute("SELECT * FROM deals")}
    flour, copper, diesel = rows["10"], rows["11"], rows["12"]
    # tovar TN VED bo'yicha yagona nom, asl nom saqlanadi; ishtirokchi nomi INN orqali
    assert flour["instrument"] == "110100" and flour["instrument_name"] == "Мука пшеничная"
    assert flour["product_name"] == "МУКА ПШЕНИЧНАЯ 1 сорт" and flour["seller"] == '"Alfa" MChJ' and flour["buyer"] == "BETA MCHJ"
    assert flour["price"] == 5000 and flour["amount_uzs"] == 5_000_000 and flour["payment_date"] == "2025-01-05"
    # USD bitim: summa USD da, so'mdagi summa bitim sanasidagi kurs bo'yicha
    assert copper["currency"] == "USD" and copper["amount"] == 20000.5 and copper["amount_uzs"] == 260_006_500
    # dizel kg -> tonna, narx tonnaga
    assert diesel["instrument"] == "271019-DT" and diesel["unit"] == "тонна" and diesel["quantity"] == 5
    assert diesel["price"] == 12_000_000 and diesel["payment_date"] is None
    assert con.execute("SELECT COUNT(*) FROM contracts").fetchone()[0] == 3


def test_turnover_excludes_cancelled(tmp_path, data):
    con = db.connect(tmp_path / "t.db")
    uzex.load(con, data)
    ov = market.overview(con)
    assert ov["total_deals"] == 3 and ov["month_deals"] == 2 and ov["month_turnover"] == 265_006_500
    d = market.deals(con, q="мука")  # kirill harflarida katta-kichik harf farqsiz qidiruv
    assert d["total"] == 1 and d["rows"][0]["deal_id"] == "10"
    assert market.deals(con, q="900000002")["total"] == 3
    r = OfflineAgent(con).ask("Сколько сделок по муке в 2025 году?")
    assert "1 сделок" in r.answer and "5 000 000" in r.answer and r.verified


def test_offline_registry_questions(tmp_path, data):
    con = db.connect(tmp_path / "t.db")
    uzex.load(con, data)
    ask = lambda q: OfflineAgent(con).ask(q)
    r = ask("Какая доля аннулированных сделок в 2025 году?")
    assert "3 сделок" in r.answer and "аннулировано (не оплачено) 1" in r.answer and "33.33%" in r.answer and r.verified
    r = ask("Сколько экспортных сделок в 2025 году?")  # filtr: market = Экспортный
    assert "1 сделок" in r.answer and "260 006 500" in r.answer and r.verified
    r = ask("Сколько в среднем дней от сделки до оплаты?")
    assert "в среднем 3.0 дн." in r.answer and r.verified
    r = ask("Какой товар самый продаваемый по сумме в 2025 году?")  # товар, а не продавец
    assert r.answer.splitlines()[1].startswith("1. Медный катод") and r.verified
