"""Oflayn agent (LLM kalitisiz): savolni qoidalar asosida SQL ga aylantiradi va FAQAT SQL natijasidan javob yozadi.

Claude API kaliti bo'lmasa yoki API xato bersa ishlaydi. Hech qanday son o'ylab topilmaydi:
javobdagi har bir son shu modul bajargan SELECT natijasidan olinadi va verify.py bilan tekshiriladi.
Savol tushunilmasa yoki ma'lumotlarda javob bo'lmasa — buni ochiq aytadi.
"""
from __future__ import annotations

import re
import sqlite3

from . import db
from .verify import check_answer

# ---------------- matn normalizatsiyasi ----------------
_TR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюяўқғҳ",
               ["a", "b", "v", "g", "d", "e", "yo", "j", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t",
                "u", "f", "x", "ts", "ch", "sh", "sh", "", "i", "", "e", "yu", "ya", "o", "q", "g", "h"]))
_APOS = re.compile(r"[’ʻʼ`‘']")


def norm(s: str) -> str:
    s = _APOS.sub("", str(s).lower())
    s = "".join(_TR.get(c, c) for c in s)
    return re.sub(r"\s+", " ", s).strip()


# ru/en so'z o'zagi -> bazadagi (o'zbekcha) nom o'zagi
ALIASES = [
    (r"\bmed[yi]|\bmedn|copper|katod", "mis katodi"), (r"tsement|cement|portlandsement", "sement portlandsement"),
    (r"pshenits|wheat|bugdoy", "bugdoy"), (r"zolot|\bgold|oltin", "oltin"), (r"\bseri\b|sulfur|oltingugurt", "oltingugurt"),
    (r"benzin|gasoline|petrol", "benzin avtobenzin"), (r"xlop|cotton|paxta", "paxta"), (r"saxar|sugar", "shakar"),
    (r"szhizh|lpg|propan|liquefied", "suyultirilgan gaz"), (r"\bug(ol|l)|coal|komir", "toshkomir"),
    (r"podsolnech|maslo|masla|sunflower|kungaboqar", "kungaboqar"), 
    (r"dizel|diesel|\bdt\b", "dizel"), (r"armatur|rebar", "armatura"), (r"polipropilen|polypropylene", "polipropilen"),
    (r"polietilen|polyethylene", "polietilen"), (r"evro|euro", "evro"),
]
# Bazada bo'lmasligi mumkin bo'lgan tovarlar — so'ralsa "ma'lumot yo'q" deyiladi
FOREIGN = [(r"zolot|\bgold|oltin", {"ru": "золото", "uz": "oltin", "en": "gold"}),
           (r"serebr|silver|kumush", {"ru": "серебро", "uz": "kumush", "en": "silver"}),
           (r"\bris\b|\brisa\b|\brice\b|guruch", {"ru": "рис", "uz": "guruch", "en": "rice"}),
           (r"myas|\bmeat|gosht", {"ru": "мясо", "uz": "go'sht", "en": "meat"}),
           (r"neft[\s-]*(syr|xom)|crude", {"ru": "сырая нефть", "uz": "xom neft", "en": "crude oil"}),
           (r"alyumin|alumin", {"ru": "алюминий", "uz": "alyuminiy", "en": "aluminium"})]

MONTHS = [  # (oy raqami, o'zaklar)
    (1, ["yanvar", "january", "jan "]), (2, ["fevral", "february"]), (3, ["mart", "march"]),
    (4, ["aprel", "april"]), (5, ["\\bmay\\b", "\\bmaya\\b", "\\bmae\\b", "\\bmay "]), (6, ["iyun", "june"]),
    (7, ["iyul", "july"]), (8, ["avgust", "august"]), (9, ["sentyabr", "sentabr", "september"]),
    (10, ["oktyabr", "oktabr", "october"]), (11, ["noyabr", "november"]), (12, ["dekabr", "december"]),
]
MONTH_NAMES = {
    "ru": ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"],
    "uz": ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
}


def detect_lang(q: str) -> str:
    if re.search(r"[а-яё]", q.lower()):
        return "ru"
    if re.search(r"\b(qancha|nechta|qaysi|yil|oy|bo.yicha|bitim|tovar|eng|uchun|necha|savdo|hajmi|o.rtacha|ta\b)", q.lower()):
        return "uz"
    return "en"


def fmt(v, d=2) -> str:
    if v is None:
        return "—"
    if float(v).is_integer() and d == 2:
        d = 0
    s = f"{float(v):,.{d}f}".replace(",", " ")
    return s


T = {
    "ru": {
        "stock_q": "Акции {t} — {issuer}, котировка на {d}: цена закрытия {c} {cur}, цена последней сделки {l} {cur}, изменение {ch} {cur} ({pct}% к базовой цене {prev}).",
        "com_q": "Котировки UZEX на {d} (средняя цена, {cur}):",
        "com_q_row": "{name} — {p} (изменение {ch}; {pct}%)",
        "q_src": "Источник: таблица {t} (файл «{f}»).",
        "nodata": "В имеющихся данных ответа на этот вопрос нет.",
        "foreign": "В данных нет сделок по товару «{x}». Доступные товары: {lst}.",
        "noperiod": "В данных нет сделок{p}. Данные охватывают период {a} — {b}.",
        "unclear": "Не удалось однозначно понять вопрос, поэтому я не отвечаю наугад. Уточните товар/тикер, период и показатель — например: «Сколько сделок по Mis katodi в 2025 году и на какую сумму?» или «Топ-5 покупателей дизельного топлива за 2024 год».",
        "sum": "{who}{per}: {n} сделок на сумму {s} {cur}, объём {q} {unit}, средневзвешенная цена {p} {cur}.",
        "sum_all": "{per}: {n} сделок на общую сумму {s} {cur}.",
        "top_amount": "Топ-{k} {dim} по сумме сделок{who}{per}:",
        "top_count": "Топ-{k} {dim} по числу сделок{who}{per}:",
        "row_amount": "{i}. {name} — {s} {cur} ({n} сделок)",
        "row_count": "{i}. {name} — {n} сделок на {s} {cur}",
        "avg": "Средневзвешенная цена{who}{per} по месяцам ({cur} за ед.):",
        "avg_row": "{m}: {p} (сделок: {n})",
        "usd": "Оборот{who}{per} в долларах (каждая сделка пересчитана по курсу USD на дату сделки): {u} USD ({s} UZS, {n} сделок).",
        "stock": "Акции {t}{per}: {n} сделок, {q} шт., объём торгов {v} {cur}; цена от {lo} до {hi}, последняя {last} ({d}).",
        "stock_none": "По акциям {t}{per} сделок в данных нет.",
        "dims": {"instrument_name": "товаров", "buyer": "покупателей", "seller": "продавцов", "region": "регионов",
                 "category": "товарных групп", "seller_broker": "брокеров продавца", "buyer_broker": "брокеров покупателя",
                 "broker": "брокеров"},
        "in": " в {x}", "for_year": " за {y} год", "for_month": " за {m} {y}", "for_range": " за {a} — {b}",
        "for_prod": " по товару «{x}»", "src": "Источник: таблица {t}, файл(ы): {f}. SQL-запросы показаны ниже.",
    },
    "uz": {
        "stock_q": "{t} aksiyalari — {issuer}, {d} kotirovkasi: yopilish narxi {c} {cur}, oxirgi bitim narxi {l} {cur}, o'zgarish {ch} {cur} (bazaviy narx {prev} ga nisbatan {pct}%).",
        "com_q": "UZEX kotirovkalari, {d} (o'rtacha narx, {cur}):",
        "com_q_row": "{name} — {p} (o'zgarish {ch}; {pct}%)",
        "q_src": "Manba: {t} jadvali («{f}» fayli).",
        "nodata": "Mavjud ma'lumotlarda bu savolga javob yo'q.",
        "foreign": "Ma'lumotlarda «{x}» tovari bo'yicha bitimlar yo'q. Mavjud tovarlar: {lst}.",
        "noperiod": "Ma'lumotlarda{p} bitimlar yo'q. Ma'lumotlar qamrovi: {a} — {b}.",
        "unclear": "Savolni aniq tushuna olmadim, shuning uchun taxminiy javob bermayman. Tovar/tiker, davr va ko'rsatkichni aniqlashtiring — masalan: «2025-yilda Mis katodi bo'yicha nechta bitim va qancha summa?»",
        "sum": "{who}{per}: {n} ta bitim, jami summa {s} {cur}, hajm {q} {unit}, o'rtacha tortilgan narx {p} {cur}.",
        "sum_all": "{per}: {n} ta bitim, jami summa {s} {cur}.",
        "top_amount": "Bitimlar summasi bo'yicha top-{k} {dim}{who}{per}:",
        "top_count": "Bitimlar soni bo'yicha top-{k} {dim}{who}{per}:",
        "row_amount": "{i}. {name} — {s} {cur} ({n} ta bitim)",
        "row_count": "{i}. {name} — {n} ta bitim, {s} {cur}",
        "avg": "O'rtacha tortilgan narx{who}{per}, oylar bo'yicha ({cur}/birlik):",
        "avg_row": "{m}: {p} (bitimlar: {n})",
        "usd": "Aylanma{who}{per} dollarda (har bir bitim o'z sanasidagi USD kursi bo'yicha): {u} USD ({s} UZS, {n} ta bitim).",
        "stock": "{t} aksiyalari{per}: {n} ta bitim, {q} dona, savdo hajmi {v} {cur}; narx {lo} — {hi}, oxirgisi {last} ({d}).",
        "stock_none": "{t} aksiyalari{per} bo'yicha ma'lumotlarda bitim yo'q.",
        "dims": {"instrument_name": "tovar", "buyer": "xaridor", "seller": "sotuvchi", "region": "hudud",
                 "category": "tovar guruhi", "seller_broker": "sotuvchi brokeri", "buyer_broker": "xaridor brokeri",
                 "broker": "broker"},
        "in": " {x} da", "for_year": " {y}-yilda", "for_month": " {y}-yil {m} oyida", "for_range": " {a} — {b} davrida",
        "for_prod": " «{x}» bo'yicha", "src": "Manba: {t} jadvali, fayl(lar): {f}. SQL so'rovlar quyida.",
    },
    "en": {
        "stock_q": "{t} shares — {issuer}, quote on {d}: close {c} {cur}, last trade {l} {cur}, change {ch} {cur} ({pct}% vs base price {prev}).",
        "com_q": "UZEX quotes on {d} (average price, {cur}):",
        "com_q_row": "{name} — {p} (change {ch}; {pct}%)",
        "q_src": "Source: table {t} (file \"{f}\").",
        "nodata": "The available data has no answer to this question.",
        "foreign": "The data has no deals for \"{x}\". Available commodities: {lst}.",
        "noperiod": "The data has no deals{p}. Data covers {a} — {b}.",
        "unclear": "I couldn't understand the question unambiguously, so I won't guess. Please specify the commodity/ticker, period and metric — e.g. \"How many Mis katodi deals in 2025 and their total amount?\"",
        "sum": "{who}{per}: {n} deals totalling {s} {cur}, quantity {q} {unit}, volume-weighted price {p} {cur}.",
        "sum_all": "{per}: {n} deals totalling {s} {cur}.",
        "top_amount": "Top-{k} {dim} by deal amount{who}{per}:",
        "top_count": "Top-{k} {dim} by number of deals{who}{per}:",
        "row_amount": "{i}. {name} — {s} {cur} ({n} deals)",
        "row_count": "{i}. {name} — {n} deals, {s} {cur}",
        "avg": "Volume-weighted price{who}{per} by month ({cur} per unit):",
        "avg_row": "{m}: {p} (deals: {n})",
        "usd": "Turnover{who}{per} in USD (each deal converted at the USD rate on its date): {u} USD ({s} UZS, {n} deals).",
        "stock": "{t} shares{per}: {n} trades, {q} shares, trading volume {v} {cur}; price {lo} to {hi}, last {last} ({d}).",
        "stock_none": "The data has no {t} trades{per}.",
        "dims": {"instrument_name": "commodities", "buyer": "buyers", "seller": "sellers", "region": "regions",
                 "category": "commodity groups", "seller_broker": "seller-side brokers", "buyer_broker": "buyer-side brokers",
                 "broker": "brokers"},
        "in": " in {x}", "for_year": " in {y}", "for_month": " in {m} {y}", "for_range": " for {a} — {b}",
        "for_prod": " for \"{x}\"", "src": "Source: table {t}, file(s): {f}. SQL queries are shown below.",
    },
}


class OfflineAgent:
    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.queries: list[str] = []
        self.evidence: list = []

    # --- SQL (har biri qayd qilinadi -> UI da ko'rsatiladi va tekshiruvga dalil bo'ladi) ---
    def sql(self, q: str, params: tuple = ()) -> list[list]:
        # parametrlarni so'rov matniga qo'yamiz — foydalanuvchi aynan bajarilgan SQL ni ko'radi
        shown = q
        for p in params:
            shown = shown.replace("?", "'" + str(p).replace("'", "''") + "'" if isinstance(p, str) else str(p), 1)
        res = db.run_select(self.con, shown)
        self.queries.append(shown)
        self.evidence.append(res)
        return res["rows"]

    def has(self, table: str) -> bool:
        return bool(self.con.execute("SELECT 1 FROM sqlite_master WHERE name=?", (table,)).fetchone())

    # --- savolni tahlil qilish ---
    def products(self, nq: str, names: list[str] | None = None) -> list[str]:
        for pat, rep in ALIASES:
            nq = re.sub(pat, " " + rep + " ", nq)
        if names is None:
            names = [r[0] for r in self.con.execute("SELECT DISTINCT instrument_name FROM deals WHERE instrument_name IS NOT NULL")]
        qtoks = re.findall(r"[a-z0-9.,%-]+", nq.replace("-", ""))
        scored = []
        for name in names:
            toks = re.findall(r"[a-z0-9.,%]+", norm(name).replace("-", ""))
            if not toks or not any(t.startswith(toks[0][:5]) for t in qtoks):
                continue
            score = sum(1 for nt in toks[1:] if any(
                (qt == nt) if re.match(r"[\d.,%]+$", nt) or len(nt) <= 3 else qt.startswith(nt[:4]) for qt in qtoks))
            scored.append((score, name))
        if not scored:
            return []
        best = max(s for s, _ in scored)
        return [n for s, n in scored if s == best]

    def period(self, nq: str, lang: str) -> tuple[str | None, str | None, str]:
        years = [int(y) for y in re.findall(r"\b(20\d\d)\b", nq)]
        month = next((m for m, pats in MONTHS if any(re.search(p, nq + " ") for p in pats)), None)
        t = T[lang]
        if re.search(r"posledn\w* mesyats|last month|oxirgi oy", nq):
            last = self.con.execute("SELECT MAX(deal_date) FROM deals").fetchone()[0]
            y, m = int(last[:4]), int(last[5:7])
            return f"{y}-{m:02d}-01", f"{y}-{m:02d}-31", t["for_month"].format(m=MONTH_NAMES[lang][m - 1], y=y)
        if month and not years:
            r = self.con.execute("SELECT MAX(substr(deal_date,1,4)) FROM deals WHERE substr(deal_date,6,2)=?", (f"{month:02d}",)).fetchone()
            years = [int(r[0])] if r and r[0] else []
        if month and years:
            y = years[0]
            return f"{y}-{month:02d}-01", f"{y}-{month:02d}-31", t["for_month"].format(m=MONTH_NAMES[lang][month - 1], y=y)
        if len(years) >= 2:
            a, b = min(years), max(years)
            return f"{a}-01-01", f"{b}-12-31", t["for_range"].format(a=a, b=b)
        if years:
            return f"{years[0]}-01-01", f"{years[0]}-12-31", t["for_year"].format(y=years[0])
        return None, None, ""

    @staticmethod
    def top_n(nq: str) -> int | None:
        m = re.search(r"\b(?:top|top-)\s*-?\s*(\d{1,2})\b|\b(\d{1,2})\s*(?:ta|ta eng|samyx|largest|biggest)\b", nq)
        if m:
            return int(m.group(1) or m.group(2))
        if re.search(r"\btop\b|samy|naibol|bolshe vsego|krupnejsh|krupneysh|eng (kop|katta|yirik)|most|largest|biggest|highest|lider", nq):
            return 5
        if re.search(r"\b(kakoj|kakoy|kakie|kakaya|qaysi|which)\b", nq):
            return 5
        return None

    @staticmethod
    def dim(nq: str) -> str | None:
        if re.search(r"broker", nq):
            if re.search(r"prodav|sotuvchi|seller", nq):
                return "seller_broker"
            if re.search(r"pokupat|xaridor|buyer", nq):
                return "buyer_broker"
            return "broker"
        if re.search(r"pokupat|xaridor|buyer|customer|zakazchik", nq):
            return "buyer"
        if re.search(r"prodav|sotuvchi|seller|proizvodit|ishlab chiqar|producer|postavsh", nq):
            return "seller"
        if re.search(r"region|hudud|viloyat|oblast|viloyat", nq):
            return "region"
        if re.search(r"grupp|guruh|categor|kategor|otrasl|soha|sektor", nq):
            return "category"
        if re.search(r"tovar|commodit|product|mahsulot", nq):
            return "instrument_name"
        return None

    # --- javob ---
    def ask(self, question: str):
        from .agent import AgentResult
        lang = detect_lang(question)
        t = T[lang]
        nq = norm(question)
        lines = self._answer(question, nq, lang, t)
        answer = "\n".join(lines)
        if len(self.queries) > 1:  # qamrov so'rovi (sanalar oralig'i) oxiriga — asosiy dalil birinchi ko'rinsin
            self.queries.append(self.queries.pop(0))
            self.evidence.append(self.evidence.pop(0))
        check = check_answer(answer, self.evidence, question)
        return AgentResult(answer, check["ok"], check["unsupported"], self.queries, self.evidence)

    def _where(self, prods, d1, d2):
        w, p = ["1=1"], []
        if prods:
            w.append("instrument_name IN (" + ",".join("?" * len(prods)) + ")"); p += prods
        if d1:
            w.append("deal_date BETWEEN ? AND ?"); p += [d1, d2]
        return " AND ".join(w), tuple(p)

    def _src(self, t, w, p) -> str:
        files = [r[0] for r in self.sql(f"SELECT DISTINCT source_file FROM deals WHERE {w} LIMIT 5", p)]
        return t["src"].format(t="deals", f=", ".join(files) or "—")

    def _answer(self, q, nq, lang, t) -> list[str]:
        cov = self.sql("SELECT MIN(deal_date), MAX(deal_date), COUNT(*) FROM deals")[0]

        # 1) aksiya tikeri: kotirovka (uzse_quotes) yoki bitimlar (stock_trades)
        has_period = bool(re.search(r"\b20\d\d\b", nq)) or any(re.search(p, nq + " ") for _, ps in MONTHS for p in ps)
        volume_q = bool(re.search(r"obem|obyom|hajm|volume|sdel|bitim|trades|kolichest|soni\b|nechta", nq))
        quote_q = bool(re.search(r"kotirov|quote|tsen|narx|price|stoim|qiymat|turadi|zakrit|yopilish|close", nq))
        q_tk = {r[0] for r in self.con.execute("SELECT ticker FROM uzse_quotes")} if self.has("uzse_quotes") else set()
        tr_tk = {r[0] for r in self.con.execute("SELECT DISTINCT ticker FROM stock_trades")} if self.has("stock_trades") else set()
        tk = next((w for w in re.findall(r"\b[A-Z]{3,6}\b", q) if w in q_tk | tr_tk), None)
        if tk:
            if tk in q_tk and (not volume_q or tk not in tr_tk):
                return self._stock_quote(tk, lang, t)
            return self._stock(tk, nq, lang, t)

        # 1b) tovar kotirovkasi (uzex_quotes) — davr ko'rsatilmagan narx savollari
        if self.has("uzex_quotes") and quote_q and not has_period and not volume_q:
            names = [r[0] for r in self.con.execute("SELECT name FROM uzex_quotes")]
            hit = self.products(nq, names)
            if hit:
                return self._commodity_quote(hit, lang, t)

        if not cov[2]:  # tovar bitimlari reyestri bo'sh
            return [t["nodata"]]

        # 2) bazada yo'q tovar
        prods = self.products(nq)
        if not prods:
            for pat, names in FOREIGN:
                if re.search(pat, nq):
                    lst = [r[0] for r in self.sql("SELECT DISTINCT instrument_name FROM deals ORDER BY 1")]
                    return [t["foreign"].format(x=names[lang], lst=", ".join(lst))]

        d1, d2, per = self.period(nq, lang)
        if d1:
            n = self.sql("SELECT COUNT(*) FROM deals WHERE deal_date BETWEEN ? AND ?", (d1, d2))[0][0]
            if not n:
                return [t["noperiod"].format(p=per, a=cov[0], b=cov[1])]
        if prods:  # tovar nomlari ham dalil sifatida qayd qilinadi (nomdagi sonlar, masalan "0,5%")
            prods = [r[0] for r in self.sql("SELECT DISTINCT instrument_name FROM deals WHERE instrument_name IN ("
                                             + ",".join("?" * len(prods)) + ") ORDER BY 1", tuple(prods))]
        who = t["for_prod"].format(x=", ".join(prods)) if prods else ""
        w, p = self._where(prods, d1, d2)
        k, dim = self.top_n(nq), self.dim(nq)
        by_count = bool(re.search(r"sdelok|bitim|deals|trades|chislu|soni|nechta|skolko", nq)) and not re.search(r"summ|oborot|aylanma|turnover|amount|qiymat", nq)

        # 3) dollarda
        if re.search(r"\busd\b|dollar|долл", nq) and self.has("usd_rate"):
            r = self.sql(
                "SELECT COUNT(*), ROUND(SUM(amount),2), ROUND(SUM(amount / (SELECT usd_uzs FROM usd_rate u "
                f"WHERE u.date <= d.deal_date ORDER BY u.date DESC LIMIT 1)),2) FROM deals d WHERE {w}", p)[0]
            if not r[0]:
                return [t["nodata"]]
            return [t["usd"].format(who=who, per=per, u=fmt(r[2]), s=fmt(r[1]), n=fmt(r[0])), "", self._src(t, w, p)]

        # 4) o'rtacha narx oylar bo'yicha
        if re.search(r"sredn|average|avg|ortacha|narx|tsen|price", nq) and prods:
            rows = self.sql(
                f"SELECT substr(deal_date,1,7) m, ROUND(SUM(amount)/SUM(quantity),2) vwap, COUNT(*) n, MAX(currency) "
                f"FROM deals WHERE {w} AND quantity > 0 GROUP BY m ORDER BY m", p)
            if not rows:
                return [t["nodata"]]
            out = [t["avg"].format(who=who, per=per, cur=rows[0][3] or "UZS")]
            out += [t["avg_row"].format(m=r[0], p=fmt(r[1]), n=fmt(r[2])) for r in rows[-24:]]
            return out + ["", self._src(t, w, p)]

        # 5) top-N
        if k and (dim or not prods):
            dim = dim or "instrument_name"
            order = "n DESC, s DESC" if by_count else "s DESC"
            if dim == "broker":
                rows = self.sql(
                    f"SELECT name, COUNT(*) n, ROUND(SUM(amount),2) s FROM (SELECT seller_broker name, amount FROM deals WHERE {w} "
                    f"UNION ALL SELECT buyer_broker, amount FROM deals WHERE {w}) WHERE name IS NOT NULL GROUP BY name ORDER BY {order} LIMIT ?",
                    p + p + (k,))
            else:
                rows = self.sql(f"SELECT {dim}, COUNT(*) n, ROUND(SUM(amount),2) s FROM deals WHERE {w} AND {dim} IS NOT NULL "
                                f"GROUP BY {dim} ORDER BY {order} LIMIT ?", p + (k,))
            if not rows:
                return [t["nodata"]]
            head = t["top_count" if by_count else "top_amount"].format(k=k, dim=t["dims"][dim], who=who, per=per)
            row_t = t["row_count" if by_count else "row_amount"]
            return [head] + [row_t.format(i=i, name=r[0], n=fmt(r[1]), s=fmt(r[2]), cur="UZS") for i, r in enumerate(rows, 1)] \
                + ["", self._src(t, w, p)]

        # 6) soni va summa
        if prods or d1:
            r = self.sql(f"SELECT COUNT(*), ROUND(SUM(amount),2), SUM(quantity), ROUND(SUM(amount)/SUM(quantity),2), "
                         f"MAX(unit), MAX(currency) FROM deals WHERE {w}", p)[0]
            if not r[0]:
                return [t["nodata"]]
            if prods:
                txt = t["sum"].format(who=(who.strip()[:1].upper() + who.strip()[1:]), per=per, n=fmt(r[0]),
                                      s=fmt(r[1]), q=fmt(r[2]), unit=r[4] or "", p=fmt(r[3]), cur=r[5] or "UZS")
            else:
                txt = t["sum_all"].format(per=per.strip()[:1].upper() + per.strip()[1:], n=fmt(r[0]), s=fmt(r[1]), cur=r[5] or "UZS")
            return [txt, "", self._src(t, w, p)]
        return [t["unclear"]]

    def _stock_quote(self, tk, lang, t) -> list[str]:
        r = self.sql("SELECT ticker, issuer, quote_date, close_price, last_price, change_abs, "
                     "ROUND(last_price - change_abs, 4), ROUND(change_abs / (last_price - change_abs) * 100, 2), currency, source "
                     "FROM uzse_quotes WHERE ticker=?", (tk,))[0]
        return [t["stock_q"].format(t=r[0], issuer=r[1], d=r[2], c=fmt(r[3]), l=fmt(r[4]), ch=fmt(r[5]), prev=fmt(r[6]),
                                    pct=fmt(r[7]), cur=r[8]), "", t["q_src"].format(t="uzse_quotes", f=r[9])]

    def _commodity_quote(self, names, lang, t) -> list[str]:
        rows = self.sql("SELECT name, quote_date, price, change_abs, change_pct, currency, source FROM uzex_quotes WHERE name IN ("
                        + ",".join("?" * len(names)) + ") ORDER BY rowid", tuple(names))
        out = [t["com_q"].format(d=rows[0][1], cur=rows[0][5])]
        out += [t["com_q_row"].format(name=r[0], p=fmt(r[2]), ch=fmt(r[3]), pct=fmt(r[4])) for r in rows]
        return out + ["", t["q_src"].format(t="uzex_quotes", f=rows[0][6])]

    def _stock(self, tk, nq, lang, t) -> list[str]:
        years = re.findall(r"\b(20\d\d)\b", nq)
        month = next((m for m, pats in MONTHS if any(re.search(pp, nq + " ") for pp in pats)), None)
        w, p, per = "ticker=?", [tk], ""
        last = self.con.execute("SELECT MAX(trade_time) FROM stock_trades WHERE ticker=?", (tk,)).fetchone()[0]
        if re.search(r"posledn\w* mesyats|last month|oxirgi oy", nq) and last:
            month, years = int(last[5:7]), [last[:4]]
        if month:
            y = int(years[0]) if years else int(self.con.execute(
                "SELECT MAX(substr(trade_time,1,4)) FROM stock_trades WHERE ticker=? AND substr(trade_time,6,2)=?",
                (tk, f"{month:02d}")).fetchone()[0] or 0)
            w += " AND substr(trade_time,1,7)=?"; p.append(f"{y}-{month:02d}")
            per = t["for_month"].format(m=MONTH_NAMES[lang][month - 1], y=y)
        elif years:
            w += " AND substr(trade_time,1,4)=?"; p.append(years[0]); per = t["for_year"].format(y=years[0])
        r = self.sql(f"SELECT COUNT(*), SUM(quantity), ROUND(SUM(volume),2), MIN(price), MAX(price), MAX(trade_time), "
                     f"MAX(currency) FROM stock_trades WHERE {w}", tuple(p))[0]
        if not r[0]:
            return [t["stock_none"].format(t=tk, per=per)]
        lastp = self.sql(f"SELECT price FROM stock_trades WHERE {w} ORDER BY trade_time DESC LIMIT 1", tuple(p))[0][0]
        return [t["stock"].format(t=tk, per=per, n=fmt(r[0]), q=fmt(r[1]), v=fmt(r[2]), lo=fmt(r[3]), hi=fmt(r[4]),
                                  last=fmt(lastp), d=r[5], cur=r[6] or "UZS"),
                "", T[lang]["src"].format(t="stock_trades", f="stock_trades.csv")]
