"""Birja bitimlari agenti: Claude + tool-use (SQL) + sonlarni tekshirish."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field

from . import config, db
from .verify import check_answer

SYSTEM_PROMPT = """Sen birja bitimlari bo'yicha tahlilchi AI-agentsan.

QAT'IY QOIDALAR:
1. Faqat vositalar (tools) orqali bazadagi jadvallardan (`deals` — tovar birjasi bitimlari; agar mavjud bo'lsa
   `stock_trades`, `listings`, `participants`, `brokers`, `contracts`, `usd_rate`) olingan ma'lumotlarga tayan. O'z bilimingdan,
   taxmindan yoki internetdan hech qanday fakt, son, narx, kompaniya nomini qo'shma.
2. Har qanday hisob-kitobni (yig'indi, o'rtacha, foiz, o'sish, tartiblash) SQL orqali bajar —
   boshingda hisoblama. Javobdagi har bir son SQL natijasida aynan bo'lishi kerak.
3. Avval `describe_data` bilan qamrovni (sanalar, birjalar, valyutalar) tekshir. Nom yoki tovar
   noaniq bo'lsa, `distinct_values` bilan bazadagi aniq yozilishini top.
4. Agar ma'lumotlarda javob yo'q bo'lsa (davr qamrovdan tashqarida, tovar topilmadi va h.k.),
   aniq ayt: "Mavjud ma'lumotlarda bu savolga javob yo'q" va nimasi yetishmayotganini tushuntir.
   Hech qachon taxminiy javob berma, prognoz qilma, investitsiya maslahati berma.
5. Valyutalarni aralashtirma. `amount` — shartnoma valyutasida (UZS yoki USD), `amount_uzs` — hammasi so'mda
   (USD bitimlar bitim sanasidagi kurs bo'yicha). Aylanma/summa uchun `amount_uzs` ni ishlat.
5a. Bitim holati `status`: 'Аннулирован(Не оплачен)' — bitim amalga oshmagan. Aylanma, hajm va narx hisoblarida
   ularni chiqarib tashla (status NOT LIKE 'Аннулирован%') va buni javobda ayt. Hajm `quantity` — o'lchov
   birligida (lotlar × lot hajmi), narx `price` — bir birlik uchun. Tovar nomi: `instrument_name` (yagona nom),
   `product_name` — reyestrdagi asl to'liq nom. Sotuvchi/xaridor: nom (`seller`, `buyer`) va INN (`seller_inn`, `buyer_inn`).
6. Javob oxirida "Manba:" bo'limida ishlatilgan fayl(lar) nomini va davrni yoz; zarur bo'lsa
   bitim raqamlarini (deal_id) keltir.
7. Dollarga o'tkazish kerak bo'lsa `usd_rate` jadvalidagi o'sha sananing kursini SQL ichida ishlat.
8. Foydalanuvchi qaysi tilda yozsa (o'zbek, rus, ingliz), o'sha tilda qisqa va aniq javob ber.
   Sonlarni SQL natijasidagidek yoz (yaxlitlasang, "taxminan" demasdan, masshtabni ko'rsat:
   masalan 12,49 mlrd so'm).
"""

TOOLS = [
    {
        "name": "describe_data",
        "description": "Jadval sxemasi, umumiy qatorlar soni, sanalar oralig'i, birjalar, valyutalar va yuklangan manbalar.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "distinct_values",
        "description": "Ustundagi mavjud qiymatlar (va bitimlar soni). Tovar/emitent nomining bazadagi aniq yozilishini topish uchun.",
        "input_schema": {
            "type": "object",
            "properties": {
                "column": {"type": "string", "description": "Ustun nomi, masalan instrument_name, category, region"},
                "like": {"type": "string", "description": "Ixtiyoriy qidiruv bo'lagi (katta-kichik harf farqsiz)"},
            },
            "required": ["column"],
        },
    },
    {
        "name": "run_sql",
        "description": (
            "Bazaga bitta SQLite SELECT so'rovini bajaradi (faqat o'qish). "
            "`deals` ustunlari: deal_id, deal_date (YYYY-MM-DD matn), exchange, market, instrument, instrument_name, "
            "category, quantity, unit, price, amount, currency, seller, buyer, region, seller_broker, buyer_broker, "
            "deal_time, trade_type, contract_form, status, product_name, contract_id, lots, lot_size, start_price, "
            "amount_uzs, seller_inn, buyer_inn, payment_date, delivery_date, delivered_lots, source_file, source_row. "
            "Matn qidiruvida LOWER() kirill harflari bilan ham ishlaydi. Boshqa jadvallar ustunlari describe_data -> other_tables da. "
            f"Natija ko'pi bilan {config.MAX_ROWS} qator. Agregatlar uchun SUM/AVG/COUNT/ROUND dan foydalan."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"sql": {"type": "string"}},
            "required": ["sql"],
        },
    },
]


@dataclass
class AgentResult:
    answer: str
    verified: bool
    unsupported: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    tool_results: list = field(default_factory=list)


class BirjaAgent:
    def __init__(self, con: sqlite3.Connection | None = None, client=None, model: str | None = None):
        self.con = con or db.connect(readonly=True)
        self.model = model or config.MODEL
        if client is None:
            import anthropic

            if not config.ANTHROPIC_API_KEY:
                raise RuntimeError("ANTHROPIC_API_KEY o'rnatilmagan (.env faylga yozing).")
            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.client = client

    # --- tools ---
    def _call_tool(self, name: str, args: dict):
        try:
            if name == "describe_data":
                return db.describe(self.con)
            if name == "distinct_values":
                return {"values": db.distinct_values(self.con, args["column"], args.get("like"))}
            if name == "run_sql":
                return db.run_select(self.con, args["sql"])
            return {"error": f"Noma'lum vosita: {name}"}
        except Exception as e:  # xatoni modelga qaytaramiz, u so'rovni tuzatadi
            return {"error": str(e)}

    def _loop(self, messages: list, queries: list, evidence: list) -> str:
        for _ in range(config.MAX_TOOL_ROUNDS):
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text").strip()
            results = []
            for block in resp.content:
                if block.type != "tool_use":
                    continue
                out = self._call_tool(block.name, block.input or {})
                if block.name == "run_sql":
                    queries.append(block.input.get("sql", ""))
                evidence.append(out)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(out, ensure_ascii=False, default=str)[:60000],
                })
            messages.append({"role": "user", "content": results})
        return "Kechirasiz, savolni belgilangan qadamlar ichida hal qila olmadim. Savolni aniqroq bering."

    def ask(self, question: str, history: list | None = None) -> AgentResult:
        messages = list(history or []) + [{"role": "user", "content": question}]
        queries: list[str] = []
        evidence: list = []
        answer = self._loop(messages, queries, evidence)
        check = check_answer(answer, evidence, question)
        if not check["ok"]:
            # bir marta qayta yozdiramiz
            messages.append({
                "role": "user",
                "content": (
                    "TEKSHIRUV: javobingdagi quyidagi sonlar vosita natijalarida topilmadi: "
                    + ", ".join(check["unsupported"])
                    + ". Ularni SQL bilan hisoblab tasdiqla yoki javobdan olib tashla. "
                    "Faqat ma'lumotlardagi sonlarni qoldirib, javobni qayta yoz."
                ),
            })
            answer = self._loop(messages, queries, evidence)
            check = check_answer(answer, evidence, question)
        if not check["ok"]:
            answer += (
                "\n\n⚠️ Ogohlantirish: quyidagi sonlar ma'lumotlar bilan avtomatik tasdiqlanmadi: "
                + ", ".join(check["unsupported"])
            )
        return AgentResult(answer, check["ok"], check["unsupported"], queries, evidence)
