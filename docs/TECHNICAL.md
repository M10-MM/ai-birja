# AI Birja — yechim tavsifi

Tovar birjasi bitimlari haqidagi savollarga **faqat ma'lumotlar asosida** javob beradigan AI-agent va birja sayti.
Savollar o'zbek, rus va ingliz tilida; har bir javob ostida u qaysi SQL so'rov va qaysi qatorlarga asoslangani ko'rinadi.

## 1. Ma'lumotlar

Tanlov to'plami `uzex_spot_data` ([data/uzex/uzex_spot_data.zip](../data/uzex/uzex_spot_data.zip), format —
tovar-xomashyo birjasi reyestri, ma'lumotlar o'ylab topilgan):

| fayl | hajm | nima |
|---|---|---|
| `deals_2022.csv` … `deals_2026.csv` | 500 000 bitim, 03.01.2022 — 30.10.2026 | bitimlar reyestri |
| `contracts.csv` | 6 616 | shartnoma kartochkalari: TN VED kodi, kategoriya, valyuta, lot, muddatlar |
| `participants.csv` | 14 392 | kompaniyalar: INN, nom, hudud, faoliyat, rol, QQS |
| `brokers.csv` | 120 | broker idoralari (BK001–BK120) |
| `usd_rates.csv` | 1 765 kun | dollar kursi, 01.01.2022 — 31.10.2026 |

Bundan tashqari `data/real/` — UZSE aksiyalar kotirovkalari, aksiya bitimlari, listing va likvidlik (05.11.2026).

### Import ([app/uzex.py](../app/uzex.py)) — qanday tozalanadi

1. **Har bir bitim shartnoma kartochkasi bilan bog'lanadi** (`Номер контракта`) — valyuta, TN VED kodi, kategoriya
   olinadi. 500 000 bitimning hammasi kartochkaga ega (tekshirilgan).
2. **Tovarni aniqlash.** Kartochkani sotuvchi to'ldiradi, shuning uchun bir tovar turlicha yozilgan
   («Мука», «Мука пшеничная», «МУКА ПШЕНИЧНАЯ …», «Хлопок сырец» / «Хлопок-сырец»). Tovar = **TN VED kodi**
   (40 ta kod) va yagona nom (`instrument_name`); asl yozuv `product_name` da saqlanadi. Bir kodda ikki tovar
   bo'lgan joylar ajratildi: 271019 → *Дизельное топливо* / *Мазут топочный*; benzin litrda va tonnada sotiladi →
   ikki alohida tovar (aralashtirilsa narx noto'g'ri chiqadi). Natija — 42 tovar.
3. **Birliklar.** Hajm = `Количество` (lotlar) × `Лот`; narx = summa ÷ hajm. Dizel kg va tonnada sotiladi → tonnaga
   keltirildi.
4. **Valyuta.** 148 shartnoma USD da (paxta kalavasi, mis katodining bir qismi). `amount` — asl valyutada,
   `amount_uzs` — bitim sanasidagi kurs bo'yicha so'mda. Barcha aylanmalar `amount_uzs` bo'yicha.
5. **Bitim holati.** `Аннулирован(Не оплачен)` — bitim amalga oshmagan (≈7%). Aylanma, hajm va narxlarda ular
   **hisobga olinmaydi**; bitimlar soni so'ralsa — jami soni va ulardan nechtasi bekor qilingani alohida aytiladi.
6. **Ishtirokchilar** — nom INN orqali `participants` dan; brokerlar — kod bo'yicha `brokers` dan.
7. **Sanalar** ISO formatga (`YYYY-MM-DD`), to'lov/yetkazish sanalari bo'sh bo'lsa — `NULL`.

Natija — SQLite: `deals` (31 ustun + manba fayl va qator raqami), `contracts`, `participants`, `brokers`, `usd_rate`.

## 2. AI-agent: ikki rejim

| rejim | qachon | qanday |
|---|---|---|
| **Claude + SQL** ([app/agent.py](../app/agent.py)) | `ANTHROPIC_API_KEY` o'rnatilgan | Claude vositalar orqali ishlaydi: `describe_data` (sxema, qamrov), `distinct_values` (nomning bazadagi aniq yozilishi), `run_sql` (faqat bitta `SELECT`). Har qanday erkin savol, murakkab tahlil. |
| **Oflayn dvigatel** ([app/offline.py](../app/offline.py)) | kalit yo'q yoki API xato bersa — avtomatik | Savoldan aniqlanadi: tovar (RU/UZ/EN sinonimlar va so'z o'zagi: «муке», «хлопка», «bug'doy», «copper»), davr (yil, oy, oraliq), shartlar (eksport/ichki, spot/forvard/fyuchers, auksion turi, qisman ijro), ko'rsatkich (soni, summa, top-N, o'rtacha narx, narx dinamikasi, USD da aylanma, bekor qilinganlar ulushi, holatlar, to'lov/yetkazish muddati). → tayyor SQL → javob faqat SQL natijasidan. |

Oflayn dvigatel savolni tushunmasa — **taxmin qilmaydi**, aniqlashtirishni so'raydi. Bazada yo'q tovar
(masalan, oltin) yoki qamrovdan tashqari davr so'ralsa — «ma'lumotlarda yo'q» deydi va nima borligini ko'rsatadi.
Interfeysda qaysi rejim javob bergani ko'rsatiladi.

## 3. Javoblar qanday tekshiriladi

"Faqat ma'lumotlar asosida" — to'rt qatlam:

1. **Tizim ko'rsatmasi** — model o'z bilimidan son/fakt qo'shmaydi; har bir hisob SQL bilan; valyutalarni
   aralashtirmaydi; bekor qilingan bitimlarni aylanmaga qo'shmaydi; ma'lumot bo'lmasa «javob yo'q» deydi.
2. **Faqat o'qish** — baza `mode=ro` da ochiladi; [db.py](../app/db.py) faqat bitta `SELECT`/`WITH` ga ruxsat beradi
   (`INSERT`, `DROP`, `PRAGMA` … taqiqlangan).
3. **Sonlarni avtomatik tekshirish** — [verify.py](../app/verify.py) javobdagi har bir sonni (`12,5 mlrd`,
   `1 234 567,89`, `6.87%` kabi formatlar ham) SQL natijalari bilan solishtiradi. Topilmasa — model javobni qayta
   yozadi; yana topilmasa — javob ogohlantirish bilan chiqadi. UI da «✓ tasdiqlangan» belgisi.
4. **Shaffoflik** — har bir javob ostida bajarilgan SQL so'rovlar, javob asoslangan qatorlar va manba fayllar
   (`deals_2025.csv` …). Har bir bitim sahifada manba fayl va qator raqami bilan ko'rsatiladi — qo'lda tekshirish mumkin.

Avtotestlar (`npm test`, 28 ta) aniq sonlarni tekshiradi: import (USD → so'm, kg → tonna, bekor qilinganlar),
oflayn javoblar (soni, summa, ulush, muddatlar, «товар» va «продавец» farqi), API, kabinet.

### Namuna savollar va tekshirilgan javoblar (oflayn rejim, to'liq reyestr)

Har bir javob ✓ belgisi bilan chiqadi — undagi barcha sonlar SQL natijasida bor.

| # | Savol | Javob (qisqa) |
|---|---|---|
| 1 | Сколько всего сделок в 2025 году? | 115 763 bitim (8 085 tasi bekor qilingan, summaga kirmaydi), 52 060 836 360 057 UZS |
| 2 | Какой объём торгов мукой в 2024 году? | «Мука пшеничная»: 6 816 bitim (467 bekor), 526 473 912 131 UZS, 109 538 300 kg, o'rtacha 4 806,30 UZS/kg |
| 3 | Топ-5 покупателей хлопка в 2023 году | 1. "Zoket Invest" OK — 546 183 569 025 UZS (1 313 bitim), 2. "Fo‘sor Qurilish" MChJ — 216 051 584 217 UZS … |
| 4 | Средняя цена дизельного топлива в 2025 году | oylar bo'yicha o'rtacha narx: 2025-01 — 12 760 065,65 UZS/t … |
| 5 | Доля аннулированных сделок в 2024 году | 7 323 / 106 647 = 6,87 % bitim; summa bo'yicha 6,92 % |
| 6 | Какая динамика цены цемента по годам? | «Портландцемент»: 2022 — 721 209,83 → 2026 — 1 002 625,96 UZS (+39,02 %) |
| 7 | Оборот в долларах в 2025 году | 4 201 188 537,30 USD (har bitim o'z sanasidagi kurs bo'yicha) |
| 8 | Сколько продавцов на бирже? | 14 392 kompaniya: 392 sotuvchi, 14 000 xaridor; 120 broker |
| 9 | Среднее время оплаты в 2025 году | bitimdan to'lovgacha 6,8 kun, to'lovdan yetkazishgacha 10,8 kun |
| 10 | Сколько экспортных сделок было в 2026 году? | 1 370 bitim (107 bekor), 3 039 914 268 381 UZS |

Savollarni o'zbek va ingliz tilida ham berish mumkin (masalan, «Nechta sotuvchi va xaridor bor?», «How many brokers?»).

## 4. Texnologiyalar

- **Backend:** Python 3.11+, FastAPI, SQLite, pandas.
- **AI:** Claude (Anthropic API, tool use) + o'z oflayn qoidalar → SQL dvigateli.
- **Frontend:** framework'siz HTML/CSS/JS, SVG grafiklar; RU/EN interfeys.
- **Tezlik:** indekslar (sana, tovar, INN, bitim raqami), qidiruv uchun oldindan kichik harflangan ustun,
  API natijalari kesh (baza o'zgarmaguncha); oflayn javob ≈1 s.
- **Deploy:** Docker, Render (`render.yaml`) — baza image yig'ilayotganda yaratiladi.

## 5. Sayt

| sahifa | nima bor |
|---|---|
| Bosh sahifa | tovar tikeri (oxirgi savdo kuni narxi va o'zgarishi), kunlik/oylik aylanma, dollar kursi, oylik grafik |
| Товары | 42 tovar; tovar sahifasi: oylik o'rtacha narx grafigi, eng yirik xaridorlar |
| Реестр сделок | 500 000 bitim: qidiruv (nom, INN, bitim raqami), filtrlar (tovar, guruh, hudud, holat, shartnoma shakli/turi, sana), saralash, CSV |
| Участники | 120 broker; 14 392 ishtirokchi — qidiruv (nom/INN), rol filtri, sahifalash |
| Акции | UZSE aksiyalari, likvidlik |
| AI-агент | chat: javob + ✓ belgisi + SQL + asos qatorlar + vaqt |
| Кабинет | ro'yxatdan o'tish, kuzatuv ro'yxati, savollar tarixi, fayl yuklash |

## 6. Ishga tushirish

```bash
npm run setup      # = py -m pip install -r requirements.txt
npm start          # = py cli.py serve -> http://127.0.0.1:8765 (birinchi marta baza yaratiladi, ~20 s)
npm test
```

Buyruqlar: `py cli.py uzex [papka|zip]` — reyestrni qayta yuklash; `py cli.py ask "savol" --debug` — javob va SQL;
`py cli.py sql "SELECT …"`; `py cli.py load <fayl> --exchange UZEX` — boshqa formatdagi fayl (ustunlar avtomatik moslanadi).

Claude rejimi: `.env` (yoki Render → Environment) da `ANTHROPIC_API_KEY=...`.
