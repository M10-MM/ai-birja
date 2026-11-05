"""Javobdagi har bir son ma'lumotlardan (tool natijalaridan) kelganini tekshirish.

Bu "faqat ma'lumotlar asosida" talabining kafolati: model o'zidan son o'ylab topsa,
tekshiruv uni ushlaydi va javob qayta yozdiriladi yoki ogohlantirish bilan qaytariladi.
"""
from __future__ import annotations

import math
import re
from typing import Iterable

# 1 234 567,89 | 1,234,567.89 | 1234567.89 | 12,5 | -3.2
_NUM_RE = re.compile(r"(?<![\w.])-?\d{1,3}(?:[   ,]\d{3})+(?:[.,]\d+)?(?![\w])|(?<![\w.])-?\d+(?:[.,]\d+)?(?![\w])")
_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b")
_SCALE = {
    "ming": 1e3, "тыс": 1e3, "thousand": 1e3, "k": 1e3,
    "mln": 1e6, "million": 1e6, "млн": 1e6, "mil": 1e6,
    "mlrd": 1e9, "milliard": 1e9, "billion": 1e9, "млрд": 1e9, "bn": 1e9,
    "trln": 1e12, "trillion": 1e12, "трлн": 1e12,
}


def parse_num(tok: str) -> float | None:
    s = re.sub(r"[   ]", "", tok)  # bo'sh joy — minglik ajratgich
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", "") if re.fullmatch(r"-?\d{1,3}(,\d{3})+", s) and " " not in tok else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def extract_numbers(text: str) -> list[tuple[str, float]]:
    """Matndagi sonlar (sanalar, ro'yxat raqamlari chiqarib tashlanadi), masshtab so'zlari hisobga olinadi."""
    clean = _DATE_RE.sub(" ", text)
    clean = re.sub(r"(?m)^\s*\d+[.)]\s", " ", clean)  # 1. 2) ro'yxat raqamlari
    out = []
    for m in _NUM_RE.finditer(clean):
        v = parse_num(m.group(0))
        if v is None:
            continue
        tail = clean[m.end(): m.end() + 12].strip().lower()
        for word, mult in _SCALE.items():
            if re.match(rf"{re.escape(word)}\b", tail):
                v *= mult
                break
        out.append((m.group(0).strip(), v))
    return out


def _collect(values: Iterable, bag: set[float]) -> None:
    for v in values:
        if isinstance(v, bool) or v is None:
            continue
        if isinstance(v, (int, float)):
            bag.add(float(v))
        elif isinstance(v, (list, tuple)):
            _collect(v, bag)
        elif isinstance(v, dict):
            _collect(v.values(), bag)
        elif isinstance(v, str):
            for _, n in extract_numbers(v):
                bag.add(n)


def evidence_numbers(tool_results: list) -> set[float]:
    bag: set[float] = set()
    _collect(tool_results, bag)
    return bag


def _close(a: float, b: float) -> bool:
    if a == b:
        return True
    if b == 0:
        return abs(a) < 1e-9
    # yaxlitlash: javobda "12,5 mlrd" bo'lsa, ma'lumotda 12 487 300 000 — 0.5% dan kichik farq
    rel = abs(a - b) / abs(b)
    if rel <= 0.005:
        return True
    # foizlarni 0-1 oralig'ida saqlangan bo'lsa
    return abs(a - b * 100) / max(abs(b * 100), 1e-9) <= 0.005


def check_answer(answer: str, tool_results: list, question: str = "", small_int_ok: int = 12) -> dict:
    """Natija: {'ok': bool, 'unsupported': [tokenlar]}.

    Kichik butun sonlar (<= small_int_ok, masalan "top 5"), savolning o'zida bor sonlar va
    yillar (1990-2100) tekshiruvdan ozod.
    """
    ev = evidence_numbers(tool_results)
    q_nums = {n for _, n in extract_numbers(question)}
    unsupported = []
    for tok, v in extract_numbers(answer):
        if v.is_integer() and abs(v) <= small_int_ok:
            continue
        if v.is_integer() and 1990 <= v <= 2100:
            continue
        if v in q_nums:
            continue
        if any(_close(v, e) for e in ev if math.isfinite(e)):
            continue
        unsupported.append(tok)
    return {"ok": not unsupported, "unsupported": unsupported}
