"""SINOV (demo) ma'lumotlari generatori.

DIQQAT: bu fayllardagi bitimlar va narxlar SUN'IY — faqat sayt va agentni ishga tushirib ko'rish uchun.
Haqiqiy tahlil uchun tanlov ma'lumotlar papkasini yuklang:  python cli.py load <fayl> --exchange UZEX

Yaratiladi (data/demo/):
  DEMO_uzex_deals.csv      tovar birjasi bitimlari (spot.uzex.uz ga o'xshash ustunlar)
  stock_trades.csv         fond birjasi bitimlari (aksiyalar)
  listings.csv             kotirovka varag'idagi qimmatli qog'ozlar
  participants.csv         savdo ishtirokchilari
  brokers.csv              brokerlar
  usd_rate.csv             dollar kursi
"""
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data" / "demo"

PRODUCTS = [  # kod, nomi, guruh, birlik, boshlang'ich narx (2022), yillik trend
    ("ARM-12", "Armatura 12 St 35GS", "Metall", "tonna", 7_200_000, 0.05),
    ("DT-K5", "Dizel yoqilg'isi", "Neft mahsulotlari", "tonna", 11_000_000, 0.12),
    ("DT-05", "Dizel yoqilg'isi 0,5%", "Neft mahsulotlari", "tonna", 12_500_000, 0.07),
    ("DT-EV5", "Dizel yoqilg'isi Evro-5", "Neft mahsulotlari", "tonna", 13_400_000, 0.06),
    ("AI-92", "Benzin AI-92", "Neft mahsulotlari", "tonna", 9_800_000, 0.08),
    ("COAL-SS", "Toshko'mir SS FR 50-300", "Ko'mir", "tonna", 1_100_000, 0.08),
    ("CU-CAT", "Mis katodi", "Rangli metallar", "tonna", 105_000_000, 0.12),
    ("PP-B310", "Polipropilen B-310", "Kimyo", "tonna", 14_500_000, 0.07),
    ("PP-FC550", "Polipropilen FC-550", "Kimyo", "tonna", 13_900_000, 0.06),
    ("PE-0220", "Polietilen O'220", "Kimyo", "tonna", 13_100_000, 0.05),
    ("CEM-M400", "Sement M400", "Qurilish materiallari", "tonna", 620_000, 0.06),
    ("WHEAT-3", "Bug'doy 3-sinf", "Don", "tonna", 2_600_000, 0.05),
    ("COTTON-1", "Paxta tolasi 1-nav", "Qishloq xo'jaligi", "tonna", 16_000_000, 0.04),
    ("SUGAR-W", "Shakar oq", "Oziq-ovqat", "tonna", 8_400_000, 0.07),
    ("LPG", "Suyultirilgan gaz", "Neft-gaz", "tonna", 5_100_000, 0.06),
    ("OIL-SUN", "Kungaboqar yog'i", "Oziq-ovqat", "tonna", 15_200_000, 0.03),
]
REGIONS = ["Toshkent sh.", "Toshkent vil.", "Samarqand", "Farg'ona", "Andijon", "Namangan", "Buxoro",
           "Qashqadaryo", "Surxondaryo", "Navoiy", "Xorazm", "Jizzax", "Sirdaryo", "Qoraqalpog'iston"]
SELLERS = [f"DEMO Ishlab chiqaruvchi {c}" for c in "ABCDEFGH"]
BUYERS = [f"DEMO Xaridor {i:02d} MChJ" for i in range(1, 41)]
BROKERS = [(f"BR-{i:03d}", f"DEMO Broker {i:02d}") for i in range(1, 13)]

STOCKS = [  # tiker, ISIN, emitent, turi, narx, faollik (0..1), valyuta, nominal, soni, kiritilgan sana
    ("UZMK", "UZ7021720001", "<O'zmetkombinat> AJ", "common", 4300, 0.9, "UZS", 1000, 2_100_000_000, "2013-03-14"),
    ("UZMKP", "UZ702172K016", "<O'zmetkombinat> AJ", "pref", 4150, 0.55, "UZS", 1000, 34_000_000, "2013-03-14"),
    ("UZINP", "UZ7056921008", "<O'zbekinvest> EISK AJ", "pref", 3549, 0.35, "UZS", 1000, 2_100_000, "2016-05-11"),
    ("KVTS", "UZ7025770007", "<Kvarts> AJ", "common", 3338, 0.95, "UZS", 1000, 140_000_000, "2013-03-14"),
    ("HMKB", "UZ7011340005", "<Hamkorbank> ATB", "common", 115, 1.0, "UZS", 20, 9_500_000_000, "2014-02-03"),
    ("ALKB", "UZ7044760004", "<Aloqabank> AT", "common", 4.1, 0.95, "UZS", 1, 9_800_000_000, "2015-07-20"),
    ("ALKBP", "UZ704476K019", "<Aloqabank> AT", "pref", 4.29, 0.92, "UZS", 1, 130_000_000, "2015-07-20"),
    ("IPTB", "UZ7054570005", "<Ipoteka-bank> ATIB", "common", 6.58, 1.0, "UZS", 1, 30_000_000_000, "2013-03-14"),
    ("CBSK", "UZ7038380000", "<Chilonzor buyum savdo kompleksi> AJ", "common", 4.11, 0.93, "UZS", 5, 1_600_000, "2017-09-01"),
    ("SQBN", "UZ7037560008", "<O'zsanoatqurilishbank> ATB", "common", 62, 0.97, "UZS", 25, 3_900_000_000, "2013-03-14"),
    ("AGBA", "UZ7004260004", "<Agrobank> ATB", "common", 9.2, 0.96, "UZS", 1, 21_000_000_000, "2019-06-10"),
    ("AGMKP", "UZ700420K011", "<Olmaliq KMK> AJ", "pref", 31_500, 0.9, "UZS", 1000, 3_000_000, "2013-03-14"),
    ("BIOK", "UZ7006850006", "<Biokimyo> AJ", "common", 1250, 0.91, "UZS", 1000, 7_000_000, "2014-11-19"),
    ("DORI", "UZ7012470004", "<Dori-Darmon> AJ", "common", 2850, 0.94, "UZS", 1000, 12_000_000, "2013-03-14"),
    ("QZSM", "UZ7022140002", "<Qizilqumsement> AJ", "common", 7600, 0.9, "UZS", 1000, 210_000_000, "2013-03-14"),
    ("KUMZ", "UZ7036810008", "<Qo'qon mexanika zavodi> AJ", "common", 1600, 0.6, "UZS", 1000, 5_400_000, "2018-04-02"),
    ("UZTL", "UZ7041740001", "<O'zbektelekom> AK", "common", 12_000, 0.5, "UZS", 1000, 20_000_000, "2016-08-15"),
    ("URTS", "UZ7037980008", "<O'zbekiston Respublikasi tovar-xomashyo birjasi> AJ", "common", 20_100, 0.88, "UZS", 1000, 4_200_000, "2013-03-14"),
    ("XKTB", "UZ7019330003", "<Xalq banki> ATB", "common", 0.37, 0.55, "UZS", 0.5, 2_000_000_000, "2020-01-15"),
    ("TKBN", "UZ7023870005", "<Turonbank> ATB", "common", 1150, 0.45, "UZS", 1000, 1_400_000, "2015-10-01"),
    ("MXUS", "UZ7062290001", "<Maxus> AJ", "common", 520, 0.3, "UZS", 500, 6_297_967, "2026-10-09"),
    ("NGZM", "UZ7019030009", "<Navoiyazot> AJ", "common", 1150, 0.25, "USD", 1000, 615_769, "2013-03-14"),
    ("AISK", "UZ7063400006", "<Asia Insurance> SK AJ", "common", 1100, 0.2, "UZS", 1000, 107_000_000, "2026-06-29"),
    ("JMTB", "UZ7025880004", "<Juma tumani bozori> AJ", "common", 2200, 0.15, "UZS", 1000, 450_000, "2019-12-20"),
    ("SAMB", "UZ7031240001", "<Samarqand bozori> AJ", "common", 900, 0.1, "UZS", 1000, 2_300_000, "2021-02-11"),
]


def workdays(start: date, end: date):
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def write(name, rows):
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows):>7} qator -> {path}")


def commodities():
    start, end = date(2022, 1, 3), date(2026, 10, 30)
    price = {p[0]: float(p[4]) for p in PRODUCTS}
    rows, n = [], 1
    for day in workdays(start, end):
        for code, name, cat, unit, base, trend in PRODUCTS:
            price[code] *= 1 + trend / 250 + random.gauss(0, 0.005)
        for _ in range(random.randint(10, 22)):
            code, name, cat, unit, base, trend = random.choice(PRODUCTS)
            qty = random.choice([10, 20, 20, 40, 60, 60, 80, 100, 120, 200, 300])
            p = round(price[code] * random.uniform(0.97, 1.03), -2)
            br_s, br_b = random.choice(BROKERS), random.choice(BROKERS)
            rows.append({
                "Bitim raqami": f"D{day:%y%m%d}-{n:06d}",
                "Sana": day.strftime("%d.%m.%Y"),
                "Seksiya": random.choice(["Birja savdosi", "Birja savdosi", "Eksport", "Davlat xaridlari"]),
                "Kod": code, "Tovar nomi": name, "Guruh": cat, "Miqdor": qty, "Birlik": unit,
                "Narx": int(p), "Summa": int(p * qty), "Valyuta": "UZS",
                "Sotuvchi": random.choice(SELLERS), "Xaridor": random.choice(BUYERS),
                "Hudud": random.choice(REGIONS),
                "Sotuvchi brokeri": br_s[1], "Xaridor brokeri": br_b[1],
            })
            n += 1
    write("DEMO_uzex_deals.csv", rows)


def stocks():
    start, end = date(2025, 11, 3), date(2026, 11, 5)
    price = {s[0]: float(s[4]) for s in STOCKS}
    rows = []
    # past faollikdagi aksiyalar ba'zi oylarda umuman savdo qilinmaydi (likvidlik darajasi shundan)
    month_on = {(s[0], m): random.random() < s[5] ** 0.6 for s in STOCKS for m in range(13)}
    for day in workdays(start, end):
        mi = (day.year - start.year) * 12 + day.month - start.month
        for s in STOCKS:
            tk, isin, issuer, typ, _, act, cur = s[:7]
            price[tk] *= 1 + random.gauss(0.0004, 0.012)
            if not month_on[(tk, mi)] or random.random() > max(act, 0.35):
                continue
            for _ in range(random.randint(1, int(2 + act * 10))):
                t = datetime(day.year, day.month, day.day, random.randint(10, 15), random.randint(0, 59))
                p = price[tk] * random.uniform(0.985, 1.015)
                p = round(p, 2) if p < 100 else round(p)
                q = random.choice([1, 5, 10, 14, 45, 100, 319, 1000, 5000, 23000, 87045]) if p < 50 else random.choice([1, 2, 5, 10, 25, 45, 100, 500])
                rows.append({
                    "trade_time": t.strftime("%Y-%m-%d %H:%M"), "ticker": tk, "isin": isin, "issuer": issuer,
                    "sec_type": typ, "market": "STK", "board": "G1",
                    "price": p, "quantity": q, "volume": round(p * q, 2), "currency": cur,
                })
    rows.sort(key=lambda r: r["trade_time"])
    write("stock_trades.csv", rows)
    write("listings.csv", [{
        "ticker": s[0], "isin": s[1], "issuer": s[2], "sec_type": s[3], "currency": s[6],
        "nominal": s[7], "shares": s[8], "listed_date": s[9],
    } for s in STOCKS])


def references():
    write("participants.csv", [
        {"name": n, "role": "seller", "region": random.choice(REGIONS), "inn": f"30{random.randint(1000000, 9999999)}"} for n in SELLERS
    ] + [
        {"name": n, "role": "buyer", "region": random.choice(REGIONS), "inn": f"30{random.randint(1000000, 9999999)}"} for n in BUYERS
    ])
    write("brokers.csv", [{"code": c, "name": n, "license": f"L-{random.randint(100, 999)}"} for c, n in BROKERS])
    rate, rows = 10_800.0, []
    for day in workdays(date(2022, 1, 3), date(2026, 11, 5)):
        rate *= 1 + random.gauss(0.00025, 0.0015)
        rows.append({"date": day.isoformat(), "usd_uzs": round(rate, 2)})
    write("usd_rate.csv", rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    commodities()
    stocks()
    references()
