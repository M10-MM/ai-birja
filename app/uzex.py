"""Tanlov ma'lumotlari: tovar birjasi bitimlari reyestri (uzex_spot_data) ni bazaga yuklash.

Manba — papka yoki zip: deals_2022.csv … deals_2026.csv, contracts.csv, participants.csv, brokers.csv,
usd_rates.csv (format: README.md, ma'lumotlar o'ylab topilgan). Har bir bitim shartnoma kartochkasi bilan
bog'lanadi (valyuta, TN VED kodi, kategoriya), sotuvchi/xaridor nomi INN orqali participants dan olinadi.

Tovarlar sotuvchi yozganicha turlicha nomlangan («Мука», «Мука пшеничная», «МУКА ПШЕНИЧНАЯ ...»), shuning
uchun tovar = TN VED kodi (+ o'lchov birligi). `instrument_name` — yagona nom, `product_name` — reyestrdagi asl nom.
Hajm = Количество × Лот (o'lchov birligida), narx = summa / hajm.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd

from .ingest import CANONICAL

EXCHANGE = "UZEX"
DEFAULT = Path(__file__).resolve().parent.parent / "data" / "uzex" / "uzex_spot_data.zip"

# TN VED kodi -> (tovar kodi, yagona nom). Bir kodda ikki xil tovar/birlik bo'lsa — SPLIT da ajratiladi.
COMMODITIES = {
    "100199": "Пшеница продовольственная", "100630": "Рис шлифованный", "110100": "Мука пшеничная",
    "151219": "Масло подсолнечное", "151229": "Масло хлопковое", "170199": "Сахар белый",
    "220190": "Вода питьевая", "230610": "Шрот хлопковый", "230990": "Комбикорм",
    "250100": "Соль пищевая", "252020": "Гипс строительный", "252210": "Известь",
    "252329": "Портландцемент", "271012": "Бензин автомобильный", "271112": "Газ сжиженный",
    "271320": "Битум нефтяной", "280421": "Аргон газообразный", "280430": "Азот",
    "280700": "Кислота серная", "281511": "Сода каустическая", "310210": "Карбамид",
    "310230": "Аммиачная селитра", "320810": "Эмаль", "390120": "Полиэтилен", "390210": "Полипропилен",
    "390410": "Поливинилхлорид", "391721": "Трубы полиэтиленовые", "440711": "Пиломатериалы",
    "520100": "Хлопок-сырец", "520512": "Пряжа хлопчатобумажная", "690410": "Кирпич керамический",
    "700529": "Стекло листовое", "720853": "Лист стальной горячекатаный", "721420": "Арматура",
    "721710": "Проволока арматурная", "740311": "Медный катод", "760421": "Профиль алюминиевый",
    "848210": "Подшипник", "854449": "Кабель силовой",
}
CURRENCY = {"Узбекский сум": "UZS", "Доллар США": "USD"}
KG_TO_T = {"271019-DT"}  # dizel yoqilg'isi kg va tonnada sotiladi -> tonnaga keltiriladi


def _instrument(hs: str, product: str, unit: str) -> tuple[str, str]:
    if hs == "271019":  # bir kodda mazut va dizel
        return ("271019-MZ", "Мазут топочный") if "мазут" in product.lower() else ("271019-DT", "Дизельное топливо")
    if hs == "271012" and unit == "литр":  # benzin litrda ham sotiladi — tonnadagi bilan aralashtirilmaydi
        return "271012-L", "Бензин автомобильный (литр)"
    return hs, COMMODITIES.get(hs, product)


class _Source:
    """Papka yoki zip ichidagi CSV larni nomi bo'yicha o'qish."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.zip = zipfile.ZipFile(self.path) if self.path.suffix.lower() == ".zip" else None
        names = self.zip.namelist() if self.zip else [p.name for p in self.path.iterdir()]
        self.files = {Path(n).name: n for n in names if n.lower().endswith(".csv")}

    def read(self, name: str) -> pd.DataFrame:
        if self.zip:
            return pd.read_csv(io.BytesIO(self.zip.read(self.files[name])), dtype=str, encoding="utf-8-sig")
        return pd.read_csv(self.path / name, dtype=str, encoding="utf-8-sig")

    def deal_files(self) -> list[str]:
        return sorted(n for n in self.files if n.startswith("deals_"))


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.str.replace(r"[\s ]", "", regex=True), errors="coerce")


def _date(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, format="%d.%m.%Y", errors="coerce").dt.strftime("%Y-%m-%d")


def load(con, path: Path | str | None = None) -> dict:
    src = _Source(Path(path or DEFAULT))
    if not src.deal_files():
        raise FileNotFoundError(f"deals_*.csv topilmadi: {src.path}")

    # --- ma'lumotnomalar ---
    contracts = src.read("contracts.csv")
    ct = pd.DataFrame({
        "contract_id": contracts["Номер контракта"], "product": contracts["Наименование продукта"],
        "brand": contracts["Марка товара"], "size": contracts["Размер товара"], "grade": contracts["Сорт товара"],
        "type": contracts["Тип товара"], "class": contracts["Класс товара"], "hs_code": contracts["Код ТН ВЭД"],
        "product_group": contracts["Группа товара"], "category": contracts["Категория товара"],
        "industry": contracts["Отрасль промышленности"], "unit": contracts["Единица измерения"],
        "lot_size": _num(contracts["Лот"]), "currency": contracts["Валюта"].map(CURRENCY).fillna(contracts["Валюта"]),
        "base_price": _num(contracts["Базисная цена"]), "deposit": contracts["Сумма залога"],
        "delivery_basis": contracts["Базис поставки"], "region": contracts["Регион"],
        "warehouse": contracts["Адрес склада"], "trade_type": contracts["Тип торгов"],
        "market": contracts["Тип контракта"], "contract_form": contracts["Форма контракта"],
        "payment_days": _num(contracts["Срок оплаты"]), "delivery_days": _num(contracts["Срок поставки"]),
        "packing": contracts["Упаковка"], "seller_inn": contracts["ИНН продавца"],
        "registered": _date(contracts["Дата регистрации"]), "valid_until": _date(contracts["Действует до"]),
    })
    ins = [_instrument(h, p, u) for h, p, u in zip(ct["hs_code"], ct["product"], ct["unit"])]
    ct["instrument"], ct["instrument_name"] = [i[0] for i in ins], [i[1] for i in ins]

    parts = src.read("participants.csv")
    participants = pd.DataFrame({
        "inn": parts["ИНН"], "name": parts["Наименование"], "region": parts["Регион"],
        "activity": parts["Вид деятельности"],
        "role": parts["Роль"].map({"Продавец": "seller", "Покупатель": "buyer"}).fillna(parts["Роль"]),
        "vat_payer": parts["Плательщик НДС"],
    })
    names = dict(zip(participants["inn"], participants["name"]))

    br = src.read("brokers.csv")
    brokers = pd.DataFrame({"code": br["Код брокера"], "name": br["Наименование"], "inn": br["ИНН"], "region": br["Регион"]})

    ur = src.read("usd_rates.csv")
    usd = pd.DataFrame({"date": _date(ur["Дата"]), "usd_uzs": _num(ur["Курс"])}).dropna().sort_values("date")
    rate = dict(zip(usd["date"], usd["usd_uzs"]))

    # --- bitimlar ---
    cinfo = ct.set_index("contract_id")[["instrument", "instrument_name", "category", "currency", "unit"]]
    frames, per_file = [], []
    for fname in src.deal_files():
        d = src.read(fname)
        c = cinfo.reindex(d["Номер контракта"]).reset_index(drop=True)
        lots, lot_size = _num(d["Количество"]), _num(d["Лот"])
        amount, start = _num(d["Сумма сделки"]), _num(d["Стартовая цена"])
        unit = d["Единица измерения"].copy()
        qty = lots * lot_size
        kg = c["instrument"].isin(KG_TO_T).values & (unit == "килограмм").values
        qty = qty.where(~kg, qty / 1000)
        start = start.where(~kg, start * 1000)
        unit = unit.where(~kg, "тонна")
        deal_date = _date(d["Дата сделки"])
        cur = c["currency"].fillna("UZS").values
        fx = deal_date.map(rate).astype(float)
        out = pd.DataFrame({
            "deal_id": d["Номер сделки"], "deal_date": deal_date, "exchange": EXCHANGE,
            "market": d["Тип контракта"], "instrument": c["instrument"].values,
            "instrument_name": c["instrument_name"].values, "category": c["category"].values,
            "quantity": qty, "unit": unit, "price": (amount / qty).round(4), "amount": amount, "currency": cur,
            "seller": d["ИНН продавца"].map(names), "buyer": d["ИНН покупателя"].map(names),
            "region": d["Регион"], "seller_broker": d["Брокер продавца"], "buyer_broker": d["Брокер покупателя"],
            "deal_time": d["Время сделки"], "trade_type": d["Тип торгов"], "contract_form": d["Форма контракта"],
            "status": d["Состояние сделки"], "product_name": d["Наименование товара"],
            "contract_id": d["Номер контракта"], "lots": lots, "lot_size": lot_size, "start_price": start,
            "amount_uzs": (amount.where(cur != "USD", amount * fx)).round(2),
            "seller_inn": d["ИНН продавца"], "buyer_inn": d["ИНН покупателя"],
            "payment_date": _date(d["Дата оплаты"]), "delivery_date": _date(d["Дата поставки"]),
            "delivered_lots": _num(d["Поставлено"]),
        })
        out["source_file"] = fname
        out["source_row"] = range(2, len(out) + 2)  # CSV dagi qator raqami (1-qator — sarlavha)
        out["row_hash"] = EXCHANGE + ":" + out["deal_id"].astype(str)
        out["search"] = (out["product_name"].fillna("") + " | " + out["instrument_name"].fillna("") + " | "
                         + out["seller"].fillna("") + " | " + out["buyer"].fillna("")).str.lower()
        frames.append(out[list(CANONICAL) + ["source_file", "source_row", "row_hash", "search"]])
        per_file.append({"file": fname, "rows": len(out)})
    deals = pd.concat(frames, ignore_index=True)

    # --- yozish: reyestr to'liq almashtiriladi (DEMO bitimlar o'chiriladi) ---
    con.execute("DELETE FROM deals")
    con.execute("DELETE FROM sources")
    deals.to_sql("deals", con, if_exists="append", index=False, chunksize=50_000)
    for f in per_file:
        con.execute("INSERT OR REPLACE INTO sources VALUES (?,?,?,datetime('now'),?)",
                    (f["file"], EXCHANGE, src.path.name, f["rows"]))
    ct.to_sql("contracts", con, if_exists="replace", index=False)
    participants.to_sql("participants", con, if_exists="replace", index=False)
    brokers.to_sql("brokers", con, if_exists="replace", index=False)
    usd.to_sql("usd_rate", con, if_exists="replace", index=False)
    for sql in (
        "CREATE INDEX IF NOT EXISTS ix_deals_code_date ON deals(instrument, deal_date)",
        "CREATE INDEX IF NOT EXISTS ix_deals_contract ON deals(contract_id)",
        "CREATE INDEX IF NOT EXISTS ix_deals_seller_inn ON deals(seller_inn)",
        "CREATE INDEX IF NOT EXISTS ix_deals_buyer_inn ON deals(buyer_inn)",
        "CREATE INDEX IF NOT EXISTS ix_contracts_id ON contracts(contract_id)",
        "CREATE INDEX IF NOT EXISTS ix_participants_inn ON participants(inn)",
    ):
        con.execute(sql)
    con.commit()
    return {"source": str(src.path), "deals": len(deals), "files": per_file, "contracts": len(ct),
            "participants": len(participants), "brokers": len(brokers), "usd_rates": len(usd),
            "date_range": [deals["deal_date"].min(), deals["deal_date"].max()]}
