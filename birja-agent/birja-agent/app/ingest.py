"""E'lon qilingan bitimlar fayllarini (CSV / XLSX / JSON / HTML jadval) yagona sxemaga keltirish.

Turli birjalar ustun nomlarini o'zbek, rus yoki ingliz tilida beradi. Bu yerda ular
yagona `deals` jadvali ustunlariga moslanadi. Har bir qator qaysi fayldan kelgani
`source_file` va `source_row` ustunlarida saqlanadi — agent javobida manba ko'rsatish uchun.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd

# Yagona sxema: ustun -> tavsif (agentga sxema sifatida beriladi)
CANONICAL = {
    "deal_id": "Bitim raqami (birja bergan ID)",
    "deal_date": "Bitim sanasi, YYYY-MM-DD",
    "exchange": "Birja nomi (masalan UZEX, UZSE)",
    "market": "Bozor / seksiya / savdo maydonchasi",
    "instrument": "Tovar yoki qimmatli qog'oz kodi / tikeri",
    "instrument_name": "Tovar yoki emitent nomi",
    "category": "Tovar guruhi / soha",
    "quantity": "Miqdor (son)",
    "unit": "O'lchov birligi (tonna, dona, aksiya ...)",
    "price": "Bir birlik narxi",
    "amount": "Bitim umumiy summasi",
    "currency": "Valyuta (UZS, USD ...)",
    "seller": "Sotuvchi",
    "buyer": "Xaridor",
    "region": "Hudud",
    "seller_broker": "Sotuvchi brokeri",
    "buyer_broker": "Xaridor brokeri",
}

ALIASES: dict[str, list[str]] = {
    "deal_id": ["deal_id", "id", "bitim_raqami", "bitim raqami", "№", "номер сделки", "номер",
                "contract", "shartnoma raqami", "trade id", "lot"],
    "deal_date": ["deal_date", "date", "sana", "bitim sanasi", "дата", "дата сделки", "trade date",
                  "savdo sanasi", "datetime"],
    "exchange": ["exchange", "birja", "биржа"],
    "market": ["market", "bozor", "seksiya", "section", "площадка", "секция", "рынок", "board"],
    "instrument": ["instrument", "ticker", "tiker", "symbol", "kod", "код", "тикер", "isin"],
    "instrument_name": ["instrument_name", "name", "nomi", "tovar", "tovar nomi", "emitent",
                        "наименование", "товар", "эмитент", "product", "issuer", "commodity"],
    "category": ["category", "guruh", "kategoriya", "soha", "группа", "категория", "отрасль", "sector"],
    "quantity": ["quantity", "qty", "miqdor", "hajm", "soni", "количество", "объем", "volume"],
    "unit": ["unit", "birlik", "o'lchov birligi", "ед. изм.", "единица", "ед.изм"],
    "price": ["price", "narx", "narxi", "цена", "bir birlik narxi"],
    "amount": ["amount", "summa", "jami summa", "bitim summasi", "сумма", "сумма сделки", "value",
               "turnover", "aylanma", "стоимость"],
    "currency": ["currency", "valyuta", "валюта"],
    "seller": ["seller", "sotuvchi", "продавец"],
    "buyer": ["buyer", "xaridor", "покупатель"],
    "region": ["region", "hudud", "viloyat", "регион", "область"],
    "seller_broker": ["seller_broker", "sotuvchi brokeri", "брокер продавца", "seller broker"],
    "buyer_broker": ["buyer_broker", "xaridor brokeri", "брокер покупателя", "buyer broker"],
}

NUMERIC = {"quantity", "price", "amount"}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower().replace("ʻ", "'").replace("‘", "'"))


def map_columns(columns) -> dict[str, str]:
    """Asl ustun nomi -> yagona ustun nomi."""
    lookup = {_norm(a): canon for canon, al in ALIASES.items() for a in al}
    mapping, used = {}, set()
    for col in columns:
        canon = lookup.get(_norm(col))
        if canon and canon not in used:
            mapping[col] = canon
            used.add(canon)
    return mapping


def to_number(v):
    """'1 234 567,89' / '1,234,567.89' / '12.5 mln' kabi qiymatlarni songa aylantirish."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", "").replace(" ", "")
    if not s or s in {"-", "—"}:
        return None
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else s.replace(".", "").replace(",", ".")
    elif "," in s:
        parts = s.split(",")
        s = s.replace(",", ".") if len(parts) == 2 and len(parts[1]) != 3 else s.replace(",", "")
    s = re.sub(r"[^0-9.\-eE]", "", s)
    try:
        return float(s)
    except ValueError:
        return None


def read_any(path: Path) -> pd.DataFrame:
    suf = path.suffix.lower()
    if suf == ".csv":
        for enc in ("utf-8-sig", "cp1251"):
            try:
                return pd.read_csv(path, sep=None, engine="python", encoding=enc, dtype=str)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"CSV kodlashini aniqlab bo'lmadi: {path}")
    if suf in {".xlsx", ".xls"}:
        return pd.read_excel(path, dtype=str)
    if suf == ".json":
        return pd.read_json(path, dtype=False)
    if suf in {".html", ".htm"}:
        tables = pd.read_html(path)
        return max(tables, key=len)
    raise ValueError(f"Qo'llab-quvvatlanmaydigan format: {path.suffix}")


def normalize(df: pd.DataFrame, source_file: str, exchange: str | None = None) -> pd.DataFrame:
    mapping = map_columns(df.columns)
    out = pd.DataFrame({canon: df[orig] for orig, canon in mapping.items()})
    for c in CANONICAL:
        if c not in out:
            out[c] = None
    if exchange:
        out["exchange"] = out["exchange"].fillna(exchange)
    for c in NUMERIC:
        out[c] = out[c].map(to_number)
    dates = pd.to_datetime(out["deal_date"], errors="coerce", dayfirst=True, format="mixed")
    out["deal_date"] = dates.dt.strftime("%Y-%m-%d")
    # summa yo'q bo'lsa, lekin narx*miqdor bor bo'lsa — hisoblamaymiz (faqat e'lon qilingan ma'lumot)
    for c in CANONICAL:
        if c not in NUMERIC:
            out[c] = out[c].map(lambda x: None if x is None or (isinstance(x, float) and pd.isna(x))
                                else str(x).strip() or None)
    out["source_file"] = source_file
    out["source_row"] = range(1, len(out) + 1)
    out["row_hash"] = out.apply(
        lambda r: hashlib.sha1("|".join(str(r[c]) for c in CANONICAL).encode()).hexdigest(), axis=1
    )
    unmapped = [c for c in df.columns if c not in mapping]
    out.attrs["unmapped"] = unmapped
    return out[list(CANONICAL) + ["source_file", "source_row", "row_hash"]]
