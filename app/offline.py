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


# uz/en so'z o'zagi -> bazadagi tovar nomi (ruscha, lotinga o'girilgan: norm("Мука") == "muka").
# Ruscha savollar nomga to'g'ridan-to'g'ri mos keladi.
# Har bir almashtirish ruscha va o'zbekcha nomni birga beradi — reyestr ruscha, yuklangan fayllar o'zbekcha bo'lishi mumkin.
ALIASES = [
    (r"paxta tolasi|kalava|\byarn\b", "pryaja"),
    (r"chigit yog|cottonseed oil|paxta yog|cotton oil", "maslo xlopkovoe paxta yogi"),
    (r"kungaboqar|sunflower|podsolnech", "maslo podsolnechnoe kungaboqar"),
    (r"\bpaxta|\bcotton|\bxlopok\b|\bxlopk(a|u|om|e)\b", "xlopok paxta"),
    (r"bugdoy|\bwheat|pshenits", "pshenitsa bugdoy"), (r"\bun\b|\bflour", "muka un"), (r"guruch|\brice\b", "ris guruch"),
    (r"shakar|\bsugar|\bsaxar", "saxar shakar"),
    (r"\bsement|\bcement|\btsement|portlandt?sement", "portlandtsement portlandsement sement"),
    (r"gasoline|petrol|avtobenzin|\bbenzin", "benzin avtobenzin"), (r"\bdizel|diesel|\bdt\b", "dizelnoe toplivo dizel"),
    (r"fuel oil", "mazut"), (r"\bmis\b|copper|\bkatod|\bmedn|\bmedi?\b", "medniy katod mis katodi"),
    (r"zolot|\bgold\b|\boltin\b", "oltin zoloto"), (r"\bug(ol|l)|\bcoal|komir", "toshkomir"),
    (r"rebar", "armatura"), (r"suyultirilgan gaz|\blpg\b|propan|liquefied gas|sjijenn", "gaz sjijenniy suyultirilgan gaz"),
    (r"polyethylene", "polietilen"),
    (r"polypropylene", "polipropilen"), (r"\burea\b|mochevin", "karbamid"), (r"ammonium nitrate", "ammiachnaya selitra"),
    (r"gisht|\bbrick", "kirpich"), (r"shisha|\bglass", "steklo"), (r"\btuz\b|\bsalt\b", "sol"),
    (r"yogoch|taxta|lumber|timber", "pilomateriali"), (r"alyumin|\balumin", "profil alyuminieviy"),
    (r"\bpvx\b|\bpvc\b", "polivinilxlorid"), (r"bearing", "podshipnik"), (r"\bcable", "kabel"),
    (r"\bohak|\blime\b", "izvest"), (r"gypsum", "gips"), (r"sulfuric", "kislota sernaya"),
    (r"enamel", "emal"), (r"ichimlik suv|drinking water", "voda pitevaya"), (r"omuxta yem|\bfeed\b", "kombikorm"),
]


def _stem(word: str) -> str:
    """So'z o'zagi: oxirgi unlilar olib tashlanadi, 5 harfgacha (муке/мука -> muk, медного/медный -> medn)."""
    w = word.rstrip("aeiouy") or word
    return w[:5]


# Bazada bo'lmasligi mumkin bo'lgan tovarlar — so'ralsa "ma'lumot yo'q" deyiladi
FOREIGN = [(r"zolot|\bgold|oltin", {"ru": "золото", "uz": "oltin", "en": "gold"}),
           (r"serebr|silver|kumush", {"ru": "серебро", "uz": "kumush", "en": "silver"}),
           (r"myas|\bmeat|gosht", {"ru": "мясо", "uz": "go'sht", "en": "meat"}),
           (r"neft[\s-]*(syr|xom)|crude", {"ru": "сырая нефть", "uz": "xom neft", "en": "crude oil"}),
           (r"alyumin|alumin", {"ru": "алюминий", "uz": "alyuminiy", "en": "aluminium"})]

# Savoldagi shart -> (ustun, normallashgan savoldagi naqsh, qiymat). Faqat ustun bazada bo'lsa qo'llanadi.
FILTERS = [
    ("market", r"eksport|export", "Экспортный"),
    ("market", r"vnutrenn|ichki bozor|ichki savdo|domestic", "Внутренний"),
    ("contract_form", r"forvard|forward", "Форвард"),
    ("contract_form", r"fyuchers|futures|fyucher", "Фьючерс"),
    ("contract_form", r"\bspot", "Спот"),
    ("trade_type", r"angliysk|english auction|ingliz auksion", "Английский аукцион"),
    ("trade_type", r"obratn|reverse auction|teskari auksion", "Обратный аукцион"),
    ("trade_type", r"dvustoron|double auction|ikki tomonlama", "Двусторонний аукцион"),
    ("status", r"chastichn|qisman|partial", "Исполнен(Частично)"),
]

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
        "cx": " (из них {c} аннулированы и не учтены в сумме)",
        "sum": "{who}{per}: {n} сделок{cx} на сумму {s} {cur}, объём {q} {unit}, средневзвешенная цена {p} {cur}.",
        "sum_all": "{per}: {n} сделок{cx} на общую сумму {s} {cur}.",
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
        "flt": " [{x}]",
        "cancel": "{who}{per}: всего {n} сделок, из них аннулировано (не оплачено) {c} — {pct}% сделок; сумма аннулированных {cs} UZS ({cpct}% от суммы всех сделок).",
        "status": "Состояние сделок{who}{per} (сделок, сумма UZS):",
        "status_row": "{name} — {n} ({pct}%), {s}",
        "days": "{who}{per}: от сделки до оплаты в среднем {pay} дн. ({np} оплаченных сделок), от оплаты до поставки — {dl} дн., от сделки до поставки — {tot} дн. ({nd} поставленных сделок).",
        "yearly": "Средневзвешенная цена{who}{per} по годам (UZS за ед.):",
        "yr_row": "{y}: {p} (сделок: {n})",
        "chg": "Изменение с {a} по {b}: {d} UZS ({pct}%).",
        "for_prod": " по товару «{x}»", "src": "Источник: таблица {t}, файл(ы): {f}. Суммы в UZS (USD-сделки — по курсу на дату сделки), аннулированные (неоплаченные) сделки не учитываются. SQL-запросы показаны ниже.",
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
        "cx": " (shundan {c} tasi bekor qilingan, summaga kiritilmagan)",
        "sum": "{who}{per}: {n} ta bitim{cx}, jami summa {s} {cur}, hajm {q} {unit}, o'rtacha tortilgan narx {p} {cur}.",
        "sum_all": "{per}: {n} ta bitim{cx}, jami summa {s} {cur}.",
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
        "flt": " [{x}]",
        "cancel": "{who}{per}: jami {n} ta bitim, shundan {c} tasi bekor qilingan (to'lanmagan) — bitimlarning {pct}%; bekor qilinganlar summasi {cs} UZS (barcha bitimlar summasining {cpct}%).",
        "status": "Bitimlar holati{who}{per} (bitimlar soni, summa UZS):",
        "status_row": "{name} — {n} ({pct}%), {s}",
        "days": "{who}{per}: bitimdan to'lovgacha o'rtacha {pay} kun ({np} ta to'langan bitim), to'lovdan yetkazishgacha — {dl} kun, bitimdan yetkazishgacha — {tot} kun ({nd} ta yetkazilgan bitim).",
        "yearly": "O'rtacha tortilgan narx{who}{per}, yillar bo'yicha (UZS/birlik):",
        "yr_row": "{y}: {p} (bitimlar: {n})",
        "chg": "{a} dan {b} gacha o'zgarish: {d} UZS ({pct}%).",
        "for_prod": " «{x}» bo'yicha", "src": "Manba: {t} jadvali, fayl(lar): {f}. Summalar so'mda (USD bitimlar — bitim sanasidagi kurs bo'yicha), bekor qilingan (to'lanmagan) bitimlar hisobga olinmagan. SQL so'rovlar quyida.",
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
        "cx": " ({c} of them cancelled, not counted in the amount)",
        "sum": "{who}{per}: {n} deals{cx} totalling {s} {cur}, quantity {q} {unit}, volume-weighted price {p} {cur}.",
        "sum_all": "{per}: {n} deals{cx} totalling {s} {cur}.",
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
        "flt": " [{x}]",
        "cancel": "{who}{per}: {n} deals in total, {c} of them cancelled (unpaid) — {pct}% of deals; cancelled amount {cs} UZS ({cpct}% of the total amount).",
        "status": "Deal status{who}{per} (deals, amount UZS):",
        "status_row": "{name} — {n} ({pct}%), {s}",
        "days": "{who}{per}: from deal to payment {pay} days on average ({np} paid deals), from payment to delivery {dl} days, from deal to delivery {tot} days ({nd} delivered deals).",
        "yearly": "Volume-weighted price{who}{per} by year (UZS per unit):",
        "yr_row": "{y}: {p} (deals: {n})",
        "chg": "Change from {a} to {b}: {d} UZS ({pct}%).",
        "for_prod": " for \"{x}\"", "src": "Source: table {t}, file(s): {f}. Amounts in UZS (USD deals converted at the rate on the deal date); cancelled (unpaid) deals are excluded. SQL queries are shown below.",
    },
}


AMT = "COALESCE(amount_uzs, amount)"  # so'mda (USD bitimlar bitim sanasidagi kurs bo'yicha)
OK = "COALESCE(status,'') NOT LIKE 'Аннулирован%'"  # bekor qilingan (to'lanmagan) bitimlar hisobga olinmaydi


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

    def cols(self, table: str) -> list[str]:
        return [r[1] for r in self.con.execute(f"PRAGMA table_info({table})")]

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
            if not toks or not any(t.startswith(_stem(toks[0])) for t in qtoks):
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
        # "prodav(e|ts)" — продавец/продавцов; "продаваемый товар" (prodavaem) sotuvchi emas
        if re.search(r"prodav(e|ts)|sotuvchi|seller|proizvodit|ishlab chiqar|producer|postavshik", nq):
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

    def filters(self, nq: str) -> list[tuple[str, str]]:
        """Savoldagi qo'shimcha shartlar: eksport/ichki, spot/forvard/fyuchers, auksion turi, qisman ijro."""
        cols = set(self.cols("deals"))
        out = []
        for col, pat, val in FILTERS:
            if col in cols and re.search(pat, nq):
                if col == "market" and not self.con.execute("SELECT 1 FROM deals WHERE market=? LIMIT 1", (val,)).fetchone():
                    continue
                out.append((col, val))
        return out

    def _where(self, prods, d1, d2, flt=(), ok=True):
        w, p = ([OK] if ok else ["1=1"]), []
        if prods:
            w.append("instrument_name IN (" + ",".join("?" * len(prods)) + ")"); p += prods
        if d1:
            w.append("deal_date BETWEEN ? AND ?"); p += [d1, d2]
        for col, val in flt:
            w.append(f"{col} = ?"); p.append(val)
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

        # 1b) tovar kotirovkasi (uzex_quotes) — davr ko'rsatilmagan narx savollari.
        # To'liq bitimlar reyestri yuklangan bo'lsa, narxlar sayt bilan bir xil bo'lishi uchun reyestrdan olinadi.
        registry = self.con.execute("SELECT 1 FROM deals WHERE exchange NOT LIKE '%DEMO%' AND status IS NOT NULL LIMIT 1").fetchone()
        if self.has("uzex_quotes") and not registry and quote_q and not has_period and not volume_q:
            names = [r[0] for r in self.con.execute("SELECT name FROM uzex_quotes")]
            hit = self.products(nq, names)
            if hit:
                return self._commodity_quote(hit, lang, t)

        if not cov[2]:  # tovar bitimlari reyestri bo'sh
            return [t["nodata"]]

        # 1c) ishtirokchilar / brokerlar soni (tovar va davr ko'rsatilmagan)
        count_q = re.search(r"skolko|kolichest|nechta|qancha|how many|number of|count", nq)
        who_q = re.search(r"prodav|pokupat|uchastnik|sotuvchi|xaridor|ishtirokchi|seller|buyer|participant|broker", nq)
        if count_q and who_q and not self.products(nq) and self.has("participants"):
            return self._participants_count(nq, lang)

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
        flt = self.filters(nq)
        who = t["for_prod"].format(x=", ".join(prods)) if prods else ""
        if flt:
            who += t["flt"].format(x=", ".join(v for _, v in flt))
        w, p = self._where(prods, d1, d2, flt)
        k, dim = self.top_n(nq), self.dim(nq)
        by_count = bool(re.search(r"sdelok|bitim|deals|trades|chislu|soni|nechta|skolko", nq)) and not re.search(r"summ|oborot|aylanma|turnover|amount|qiymat", nq)
        has_status = "status" in self.cols("deals")
        cap = lambda x: x.strip()[:1].upper() + x.strip()[1:]

        # 2b) bekor qilingan bitimlar ulushi
        if has_status and re.search(r"annul|bekor|cancel|otmen|neoplach|tolanmagan|unpaid", nq):
            wa, pa = self._where(prods, d1, d2, flt, ok=False)
            r = self.sql(
                f"SELECT COUNT(*), SUM(status LIKE 'Аннулирован%'), "
                f"ROUND(100.0 * SUM(status LIKE 'Аннулирован%') / COUNT(*), 2), "
                f"ROUND(SUM(CASE WHEN status LIKE 'Аннулирован%' THEN {AMT} END), 2), "
                f"ROUND(100.0 * SUM(CASE WHEN status LIKE 'Аннулирован%' THEN {AMT} END) / SUM({AMT}), 2) "
                f"FROM deals WHERE {wa}", pa)[0]
            if not r[0]:
                return [t["nodata"]]
            head = cap(who + per) or cap(t["for_range"].format(a=cov[0], b=cov[1]))
            return [t["cancel"].format(who=head, per="", n=fmt(r[0]), c=fmt(r[1] or 0), pct=fmt(r[2] or 0),
                                       cs=fmt(r[3] or 0), cpct=fmt(r[4] or 0)), "", self._src(t, wa, pa)]

        # 2c) holatlar bo'yicha taqsimot
        if has_status and re.search(r"sostoyan|status|holat", nq):
            wa, pa = self._where(prods, d1, d2, flt, ok=False)
            rows = self.sql(
                f"SELECT status, COUNT(*) n, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM deals WHERE {wa}), 2), "
                f"ROUND(SUM({AMT}), 2) FROM deals WHERE {wa} GROUP BY status ORDER BY n DESC", pa + pa)
            if not rows:
                return [t["nodata"]]
            return [t["status"].format(who=who, per=per)] + [
                t["status_row"].format(name=r[0], n=fmt(r[1]), pct=fmt(r[2]), s=fmt(r[3])) for r in rows] \
                + ["", self._src(t, wa, pa)]

        # 2d) to'lov va yetkazish muddatlari (kunlarda)
        if has_status and re.search(r"\bdn|\bden|\bday|\bkun|srok|muddat|vremya|qancha vaqt|how long|skolko vremeni", nq) \
                and re.search(r"oplat|tolov|tolan|pay|postav|yetkaz|deliver", nq):
            r = self.sql(
                f"SELECT ROUND(AVG(julianday(payment_date) - julianday(deal_date)), 1), COUNT(payment_date), "
                f"ROUND(AVG(julianday(delivery_date) - julianday(payment_date)), 1), "
                f"ROUND(AVG(julianday(delivery_date) - julianday(deal_date)), 1), COUNT(delivery_date) "
                f"FROM deals WHERE {w}", p)[0]
            if not r[1]:
                return [t["nodata"]]
            head = cap(who + per) or cap(t["for_range"].format(a=cov[0], b=cov[1]))
            return [t["days"].format(who=head, per="", pay=fmt(r[0], 1), np=fmt(r[1]), dl=fmt(r[2], 1),
                                     tot=fmt(r[3], 1), nd=fmt(r[4])), "", self._src(t, w, p)]

        # 3) dollarda
        if re.search(r"\busd\b|dollar|долл", nq) and self.has("usd_rate"):
            r = self.sql(
                f"SELECT COUNT(*), ROUND(SUM({AMT}),2), ROUND(SUM({AMT} / (SELECT usd_uzs FROM usd_rate u "
                f"WHERE u.date <= d.deal_date ORDER BY u.date DESC LIMIT 1)),2) FROM deals d WHERE {w}", p)[0]
            if not r[0]:
                return [t["nodata"]]
            return [t["usd"].format(who=who, per=per, u=fmt(r[2]), s=fmt(r[1]), n=fmt(r[0])), "", self._src(t, w, p)]

        # 4) o'rtacha narx oylar bo'yicha
        if re.search(r"sredn|average|avg|ortacha|narx|tsen|price", nq) and prods:
            rows = self.sql(
                f"SELECT substr(deal_date,1,7) m, ROUND(SUM({AMT})/SUM(quantity),2) vwap, COUNT(*) n, 'UZS' "
                f"FROM deals WHERE {w} AND quantity > 0 GROUP BY m ORDER BY m", p)
            if not rows:
                return [t["nodata"]]
            change_q = re.search(r"izmeni|change|ozgar|dinamik|\brost|vyros|snizi|osish|trend", nq)
            if len(rows) <= 24 and not change_q:
                out = [t["avg"].format(who=who, per=per, cur=rows[0][3] or "UZS")]
                out += [t["avg_row"].format(m=r[0], p=fmt(r[1]), n=fmt(r[2])) for r in rows]
                return out + ["", self._src(t, w, p)]
            # uzun davr yoki o'zgarish savoli: yillar bo'yicha + birinchi va oxirgi yil orasidagi o'zgarish
            yrs = self.sql(
                f"SELECT substr(deal_date,1,4) y, ROUND(SUM({AMT})/SUM(quantity),2) vwap, COUNT(*) n "
                f"FROM deals WHERE {w} AND quantity > 0 GROUP BY y ORDER BY y", p)
            out = [t["yearly"].format(who=who, per=per)]
            out += [t["yr_row"].format(y=r[0], p=fmt(r[1]), n=fmt(r[2])) for r in yrs]
            if len(yrs) > 1:
                c = self.sql(
                    f"WITH y AS (SELECT substr(deal_date,1,4) y, SUM({AMT})/SUM(quantity) v FROM deals "
                    f"WHERE {w} AND quantity > 0 GROUP BY y) "
                    f"SELECT (SELECT MIN(y) FROM y), (SELECT MAX(y) FROM y), "
                    f"ROUND((SELECT v FROM y ORDER BY y DESC LIMIT 1) - (SELECT v FROM y ORDER BY y LIMIT 1), 2), "
                    f"ROUND(100.0 * ((SELECT v FROM y ORDER BY y DESC LIMIT 1) / (SELECT v FROM y ORDER BY y LIMIT 1) - 1), 2)", p)[0]
                out += ["", t["chg"].format(a=c[0], b=c[1], d=fmt(c[2]), pct=fmt(c[3]))]
            return out + ["", self._src(t, w, p)]

        # 5) top-N
        if k and (dim or not prods):
            dim = dim or "instrument_name"
            order = "n DESC, s DESC" if by_count else "s DESC"
            if dim == "broker":
                bname = ("COALESCE((SELECT b.name || ' (' || x.code || ')' FROM brokers b WHERE b.code = x.code), x.code)"
                         if self.has("brokers") and "code" in self.cols("brokers") else "x.code")
                rows = self.sql(
                    f"SELECT {bname}, COUNT(*) n, ROUND(SUM(a),2) s FROM (SELECT seller_broker code, {AMT} a FROM deals WHERE {w} "
                    f"UNION ALL SELECT buyer_broker, {AMT} FROM deals WHERE {w}) x WHERE x.code IS NOT NULL GROUP BY x.code ORDER BY {order} LIMIT ?",
                    p + p + (k,))
            else:
                rows = self.sql(f"SELECT {dim}, COUNT(*) n, ROUND(SUM({AMT}),2) s FROM deals WHERE {w} AND {dim} IS NOT NULL "
                                f"GROUP BY {dim} ORDER BY {order} LIMIT ?", p + (k,))
            if not rows:
                return [t["nodata"]]
            head = t["top_count" if by_count else "top_amount"].format(k=k, dim=t["dims"][dim], who=who, per=per)
            row_t = t["row_count" if by_count else "row_amount"]
            return [head] + [row_t.format(i=i, name=r[0], n=fmt(r[1]), s=fmt(r[2]), cur="UZS") for i, r in enumerate(rows, 1)] \
                + ["", self._src(t, w, p)]

        # 6) soni va summa
        if prods or d1 or flt:
            # soni — barcha bitimlar (bekor qilinganlar ham, alohida ko'rsatiladi); summa, hajm, narx — bekor qilinganlarsiz
            wa, pa = self._where(prods, d1, d2, flt, ok=False)
            cancelled = "status LIKE 'Аннулирован%'" if has_status else "0"
            r = self.sql(f"SELECT COUNT(*), ROUND(SUM(CASE WHEN {OK} THEN {AMT} END),2), SUM(CASE WHEN {OK} THEN quantity END), "
                         f"ROUND(SUM(CASE WHEN {OK} THEN {AMT} END)/SUM(CASE WHEN {OK} THEN quantity END),2), "
                         f"MAX(unit), 'UZS', SUM({cancelled}) FROM deals WHERE {wa}", pa)[0]
            if not r[0]:
                return [t["nodata"]]
            cx = t["cx"].format(c=fmt(r[6])) if r[6] else ""
            if prods:
                txt = t["sum"].format(who=cap(who), per=per, n=fmt(r[0]), cx=cx,
                                      s=fmt(r[1]), q=fmt(r[2]), unit=r[4] or "", p=fmt(r[3]), cur=r[5] or "UZS")
            else:
                txt = t["sum_all"].format(per=cap(who + per), n=fmt(r[0]), cx=cx, s=fmt(r[1]), cur=r[5] or "UZS")
            return [txt, "", self._src(t, wa, pa)]
        return [t["unclear"]]

    def _participants_count(self, nq, lang) -> list[str]:
        r = self.sql("SELECT COUNT(*) AS total, SUM(role = 'seller') AS sellers, SUM(role = 'buyer') AS buyers FROM participants")[0]
        total, sellers, buyers = r[0], r[1] or 0, r[2] or 0
        brokers = self.sql("SELECT COUNT(*) AS brokers FROM brokers")[0][0] if self.has("brokers") else 0
        n = lambda v: fmt(v, 0)
        if lang == "en":
            out = [f"The participant registry has {n(total)} companies: {n(sellers)} sellers and {n(buyers)} buyers."]
            if brokers: out.append(f"Broker offices: {n(brokers)}.")
            out.append("Source: participants.csv, brokers.csv.")
        elif lang == "uz":
            out = [f"Ishtirokchilar reyestrida {n(total)} ta kompaniya: {n(sellers)} ta sotuvchi va {n(buyers)} ta xaridor."]
            if brokers: out.append(f"Broker idoralari: {n(brokers)} ta.")
            out.append("Manba: participants.csv, brokers.csv.")
        else:
            out = [f"В реестре участников {n(total)} компаний: {n(sellers)} продавцов и {n(buyers)} покупателей."]
            if brokers: out.append(f"Брокерских контор: {n(brokers)}.")
            out.append("Источник: participants.csv, brokers.csv.")
        return out

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
