# AI Birja — birja ma'lumotlari sayti va AI-agent

Birja bitimlari, aksiyalar va tovar kotirovkalari bo'yicha savollarga **faqat ma'lumotlar asosida** javob beradigan
AI-agent va birja sayti prototipi (RU / EN interfeys, agent RU / UZ / EN savollarni tushunadi).

## Topshiriq uchun ma'lumot

| | |
|---|---|
| **Prototip havolasi** | _yozing: https://..._ (lokal ishga tushirish — pastda) |
| **Jamoa a'zolari** | 1. Mirakbar Mirzaraimov · 2. Bakhtiyor Parpiev · 3. Dilshod Fayzullaev |
| **Yechim tavsifi** | quyida va saytdagi «О решении» sahifasida |

## Onlayn ishga tushirish (1 klik)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/M10-MM/ai-birja)

Render bepul tarifida sayt `https://ai-birja-xxxx.onrender.com` ko'rinishidagi havolada ishlaydi (Docker, `render.yaml`).

## Ishga tushirish (lokal)

Talablar: Python 3.11+ (Windows: `py`), ixtiyoriy Node.js (faqat `npm` qisqa buyruqlari uchun).

```bash
git clone <ushbu repo>
cd <repo>
npm run setup      # = py -m pip install -r requirements.txt
npm start          # = py cli.py serve  -> http://127.0.0.1:8765
npm test           # 27 ta avtotest
```

npm bo'lmasa: `py -m pip install -r requirements.txt && py cli.py serve`
(macOS/Linux: `python3`). Birinchi ishga tushirishda baza avtomatik yaratiladi. Port band bo'lsa, server o'zi bo'sh portni tanlaydi.

Ixtiyoriy: `.env` faylida (namuna: `.env.example`) `ANTHROPIC_API_KEY=...` bo'lsa, agent Claude bilan ishlaydi;
bo'lmasa — o'rnatilgan oflayn dvigatel (qoidalar → SQL) ishlaydi.

## Yechim qisqacha

- **Texnologiyalar:** Python, FastAPI, SQLite, pandas; Claude (Anthropic API, tool use) yoki oflayn qoidalar → SQL dvigateli;
  frontend — framework'siz HTML/CSS/JS, SVG grafiklar.
- **O'ylab topmaslik kafolati:** har bir hisob — faqat o'qish rejimidagi bitta `SELECT`; javobdagi har bir son
  `verify.py` bilan SQL natijalariga solishtiriladi (tasdiqlanmasa — qayta yoziladi yoki ogohlantirish);
  ma'lumot bo'lmasa agent «ma'lumotlarda javob yo'q» deydi; savol tushunilmasa — taxmin qilmaydi.
- **Shaffoflik:** har bir javob ostida ✓ tekshiruv belgisi, SQL so'rovlar va javob asoslangan qatorlar ko'rsatiladi.
- **Sayt:** tovar tikeri, aksiyalar, tovar kotirovkalari, bitimlar reyestri (filtr, CSV), likvidlik, ishtirokchilar,
  dollar kursi, shaxsiy kabinet (ro'yxatdan o'tish, kuzatuv ro'yxati, savollar tarixi, fayl yuklash).

Batafsil texnik hujjat: [docs/TECHNICAL.md](docs/TECHNICAL.md)

## Kod tuzilmasi

| papka / fayl | nima |
|---|---|
| [app/agent.py](app/agent.py) | Claude agenti (tool use: SQL) |
| [app/offline.py](app/offline.py) | oflayn dvigatel: savol → SQL → javob (LLM kalitisiz) |
| [app/verify.py](app/verify.py) | javobdagi har bir sonni SQL natijalari bilan tekshirish |
| [app/api.py](app/api.py) | FastAPI: sayt API, `/api/ask`, kabinet |
| [app/market.py](app/market.py), [app/db.py](app/db.py), [app/ingest.py](app/ingest.py) | ma'lumotlar: yuklash, normallashtirish, so'rovlar |
| [app/auth.py](app/auth.py) | shaxsiy kabinet (ro'yxatdan o'tish, kuzatuv, tarix) |
| [app/static/](app/static/) | sayt (HTML/CSS/JS, RU/EN) |
| [data/real/](data/real/) | haqiqiy kotirovkalar (UZEX, UZSE) |
| [tests/](tests/) | avtotestlar (`npm test`) |
| [cli.py](cli.py) | buyruqlar: `serve`, `load`, `demo`, `uzex`, `ask`, `sql` |
| [app/uzex.py](app/uzex.py) | tanlov reyestri (uzex_spot_data) importi |
| [data/uzex/](data/uzex/) | tanlov ma'lumotlari (zip) |

## Ma'lumotlar

- `data/real/` — 05.11.2026 holatiga UZEX tovar kotirovkalari (27), UZSE aksiyalar (71), aksiya bitimlari, listing, likvidlik
  («Данные торгов биржи UZEX.pdf» va uzse.uz dan).
- `data/uzex/uzex_spot_data.zip` — tanlov ma'lumotlari: tovar birjasi bitimlari reyestri (500 000 bitim, 03.01.2022 — 30.10.2026),
  shartnoma kartochkalari (6 616), ishtirokchilar (14 392), brokerlar (120), dollar kursi. Ma'lumotlar o'ylab topilgan,
  format — tovar-xomashyo birjasi reyestri. `py cli.py demo` (va Docker yig'ilishi) ularni avtomatik yuklaydi;
  boshqa papka yoki zip: `py cli.py uzex <yo'l>`.
  - Tovar = TN VED kodi (sotuvchilar bir tovarni turlicha yozgan); asl nom `product_name` da saqlanadi.
  - Hajm = lotlar × lot hajmi, narx = summa / hajm. USD bitimlar so'mga bitim sanasidagi kurs bo'yicha (`amount_uzs`).
  - Aylanma va narxlarda bekor qilingan (to'lanmagan) bitimlar hisobga olinmaydi.
- Zip bo'lmasa — sun'iy DEMO reyestr yaratiladi.
