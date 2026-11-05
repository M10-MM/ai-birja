# Birja bitimlari AI-agenti

Birja bitimlari haqidagi savollarga **aniq va faqat ma'lumotlar asosida** javob beradigan AI-agent.
O'zbek, rus va ingliz tilidagi savollarni tushunadi.

## Ishga tushirish (eng oson)

`D:\AI Birja` papkasida:

```
npm run setup   # Python kutubxonalarini o'rnatadi (bir marta)
npm start       # sayt: http://127.0.0.1:8765 (baza bo'lmasa DEMO ma'lumot yaratiladi)
npm test        # testlar
```

## Haqiqiy ma'lumotlar (`data/real/`)

| fayl | jadval | manba |
|---|---|---|
| `uzex_quotes.csv` | 27 ta UZEX tovar kotirovkasi (narx, o'zgarish, %) | «Данные торгов биржи UZEX.pdf», 05.11.2026 |
| `uzse_quotes.csv` | 71 ta UZSE aksiyasi (yopilish, oxirgi bitim, o'zgarish) | o'sha PDF |
| `stock_trades.csv` | 05.11.2026 dagi 20 ta aksiya bitimi | uzse.uz «Итоги торгов» |
| `listings.csv`, `liquidity.csv` | kotirovka varag'i, likvidlik (108 / 54 / 11 / 43) | uzse.uz |

`python cli.py loadref data/real` — yuklash (`demo` buyrug'i ham ularni avtomatik ustidan yozadi).
Sayt va agent bu jadvallar bo'lsa ulardan foydalanadi; tovar bitimlari reyestri, ishtirokchilar, brokerlar va
dollar kursi hozircha DEMO — tanlov papkasi bilan almashtiring.

## AI-agent: ikki rejim

1. **Claude + SQL** — `.env` da `ANTHROPIC_API_KEY` bo'lsa. Erkin savollar, murakkab tahlil.
2. **Oflayn dvigatel** (`app/offline.py`) — kalit bo'lmasa yoki API xato bersa avtomatik ishlaydi. Savoldan tovar
   (RU/UZ/EN sinonimlar: «дизель», «медь», «пшеница»…), tiker, davr (yil/oy), ko'rsatkich (soni, summa, top-N,
   o'rtacha narx, USD da aylanma) aniqlanadi → SQL → javob faqat SQL natijasidan. Tushunmasa — taxmin qilmaydi,
   aniqlashtirishni so'raydi; bazada yo'q tovar/davr bo'lsa — «ma'lumot yo'q» deydi.

Ikkala rejimda ham javobdagi har bir son `verify.py` bilan tekshiriladi, UI da qaysi rejim ishlagani ko'rsatiladi.

## Sayt (prototip)

`python cli.py serve --port 8765` → http://127.0.0.1:8765 — RU/EN interfeys (`?lang=en`), agent RU/UZ/EN savollarni tushunadi.

| Sahifa | Nima bor |
|---|---|
| Bosh sahifa | tovar tikeri (yuqori qora lenta), kunlik/oylik aylanma, dollar kursi, "Итоги торгов", likvidlik darajalari, kotirovka varag'i, oylik aylanma grafigi |
| Акции / Stocks | barcha aksiyalar: narx, o'zgarish, hajm, kapitallashuv, likvidlik (12 oydan nechtasida savdo bo'lgan) + har bir aksiya sahifasi (grafik, oxirgi bitimlar) |
| Товары / Commodities | tovarlar kotirovkasi + tovar sahifasi (oylik o'rtacha narx, eng yirik xaridorlar) |
| Реестр сделок / Deal registry | filtrlar, saralash, sahifalash, CSV yuklab olish; har bitimda manba fayl va qator |
| Участники | ishtirokchilar va brokerlar |
| AI-агент | chat: javob + "✓ tasdiqlangan" belgisi + SQL so'rovlar + javob asoslangan qatorlar + javob vaqti |
| Кабинет | ro'yxatdan o'tish/kirish (rol tanlash), kuzatuv ro'yxati (★), agentga berilgan savollar tarixi, fayl yuklash |
| О решении | yechim tavsifi: texnologiyalar, usullar, javoblar qanday tekshirilgani |

DEMO ma'lumot (sun'iy): `python cli.py demo`. Haqiqiy ma'lumot: `python cli.py load <fayl> --exchange UZEX`
va qo'shimcha jadvallar (aksiyalar, ishtirokchilar, brokerlar, dollar kursi) uchun `python cli.py loadref <papka>`
(fayl nomlari: `stock_trades.csv`, `listings.csv`, `participants.csv`, `brokers.csv`, `usd_rate.csv`).

## Qanday ishlaydi

```
E'lon qilingan fayllar (CSV/XLSX/JSON/HTML)
        │  ingest.py — ustunlarni yagona sxemaga moslash (uz/ru/en nomlar)
        ▼
SQLite `deals` jadvali (+ har qatorning manba fayli va qator raqami)
        │
        ▼
Claude (tool-use) ── describe_data / distinct_values / run_sql (faqat SELECT)
        │
        ▼
verify.py — javobdagi HAR BIR son SQL natijalarida bormi? 
        ├─ ha  → javob ✓ tasdiqlangan
        └─ yo'q → model qayta yozadi; yana topilmasa — ogohlantirish bilan
```

"Faqat ma'lumotlar asosida" kafolati uch qatlamdan iborat:

1. **Tizim ko'rsatmasi** — model o'z bilimidan son/fakt qo'shmaydi, hisob-kitobni SQL bilan qiladi, ma'lumot bo'lmasa "javob yo'q" deydi.
2. **Faqat o'qish** — baza `mode=ro` da ochiladi, SQL tekshiruvchi faqat bitta `SELECT/WITH` ga ruxsat beradi.
3. **Sonlarni avtomatik tekshirish** — javobdagi sonlar (`12,5 mlrd`, `1 234 567,89` kabi formatlar ham) tool natijalari bilan solishtiriladi.

## Tez boshlash

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # ANTHROPIC_API_KEY ni yozing

# 1) Ma'lumot yuklash — haqiqiy e'lon qilingan fayllar:
python cli.py load data/raw/uzex_oktyabr.xlsx --exchange UZEX
#    yoki sources.json ga havolalarni yozib:  python cli.py sync
#    yoki sinab ko'rish uchun DEMO (sun'iy) ma'lumot:
python scripts/make_demo_data.py && python cli.py load data/demo/DEMO_uzex_deals.csv --exchange UZEX-DEMO

# 2) Savol berish
python cli.py ask "Oktyabr oyida summasi bo'yicha eng katta 5 ta tovar qaysi?" --debug
python cli.py chat
python cli.py serve        # http://127.0.0.1:8000 — veb interfeys, fayl yuklash bilan
```

Docker: `docker build -t birja-agent . && docker run -p 8000:8000 --env-file .env -v $PWD/data:/app/data birja-agent`

## Ma'lumot manbalari

Loyiha hech qanday ma'lumotni o'ylab topmaydi. Birjalar (masalan, UZEX — Respublika tovar xom-ashyo birjasi, UZSE — "Toshkent" RFB) rasmiy saytlarida e'lon qilgan bitimlar fayllarini yoki jadvalli sahifalarni:

- `data/raw/` ga qo'yib `cli.py load` qiling, yoki
- havolasini `sources.json` ga yozib (`"enabled": true`) `cli.py sync` qiling, yoki
- veb interfeysdan yuklang.

Ustun nomlari avtomatik moslanadi (`app/ingest.py` → `ALIASES`). Yangi format kelsa — o'sha ro'yxatga nomni qo'shing. `load` natijasidagi `unmapped_columns` qaysi ustunlar tanilmaganini ko'rsatadi.

`data/demo/` dagi fayl **sun'iy** — faqat test uchun; ishga tushirishdan oldin `data/birja.db` ni o'chirib, haqiqiy ma'lumot yuklang.

## Yagona sxema (`deals`)

| ustun | ma'nosi |
|---|---|
| deal_id, deal_date (YYYY-MM-DD) | bitim raqami, sanasi |
| exchange, market | birja, seksiya |
| instrument, instrument_name, category | kod/tiker, nomi, guruh |
| quantity, unit, price, amount, currency | miqdor, birlik, narx, summa, valyuta |
| seller, buyer, region | sotuvchi, xaridor, hudud |
| source_file, source_row | manba fayl va qator — javobda keltiriladi |

## API

- `POST /api/ask` `{"question": "..."}` → `{answer, verified, unsupported, queries}`
- `GET /api/data` → qamrov (sanalar, birjalar, manbalar)
- `POST /api/upload` (multipart `file`, ixtiyoriy `?exchange=UZEX`)

## Testlar

```bash
pytest -q     # API kalitsiz ishlaydi (soxta model mijozi bilan)
```

## Tuzilma

```
app/config.py      sozlamalar (.env)
app/ingest.py      fayllarni o'qish va normallashtirish
app/db.py          SQLite, xavfsiz SELECT, qamrov
app/verify.py      sonlarni tekshirish
app/agent.py       Claude tool-use sikli + qayta yozdirish
app/sources/fetch.py  sources.json dan yuklab olish
app/api.py, app/static/index.html   veb
cli.py             buyruq qatori
```

## Keyingi qadamlar (davom ettirish uchun)

- Aniq birja portallari uchun maxsus yuklovchilar (`app/sources/uzex.py`, `uzse.py`) va kunlik avtomatik yangilash
- Telegram bot
- Savol-javob baholash to'plami (evals) — aniqlikni o'lchash
- Grafiklar (vaqt bo'yicha narx/hajm)
