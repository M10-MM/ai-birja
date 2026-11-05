"""Buyruq qatori:

  python cli.py load data/raw/fayl.xlsx --exchange UZEX   # faylni bazaga yuklash
  python cli.py sync                                      # sources.json dagi havolalardan yuklash
  python cli.py info                                      # bazadagi qamrov
  python cli.py sql "SELECT COUNT(*) FROM deals"          # to'g'ridan-to'g'ri SELECT
  python cli.py ask "Oktyabrda jami savdo hajmi qancha?"  # agentga savol
  python cli.py chat                                      # interaktiv suhbat
  python cli.py demo                                      # DEMO ma'lumotlarni yaratib yuklash
  python cli.py loadref data/demo                         # aksiyalar/ishtirokchilar/brokerlar/kurs CSV lari
  python cli.py serve                                     # veb interfeys: http://localhost:8000
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app import db


def free_port(host: str, start: int) -> int:
    """Birinchi bo'sh portni topadi: start, start+1, ... va zaxira portlar (Windows band qilgan portlar o'tkazib yuboriladi)."""
    import socket
    for port in [*range(start, start + 10), 5050, 3001, 8080, 8888, 9000]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:  # WinError 10013 / 10048 — band yoki ruxsat yo'q
                continue
    raise SystemExit("Bo'sh port topilmadi: --port bilan boshqa port bering")


def main() -> None:
    p = argparse.ArgumentParser(description="Birja bitimlari AI-agenti")
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("load"); pl.add_argument("files", nargs="+"); pl.add_argument("--exchange")
    sub.add_parser("sync")
    sub.add_parser("demo")
    pr = sub.add_parser("loadref"); pr.add_argument("folder")
    sub.add_parser("info")
    ps = sub.add_parser("sql"); ps.add_argument("query")
    pa = sub.add_parser("ask"); pa.add_argument("question"); pa.add_argument("--debug", action="store_true")
    sub.add_parser("chat")
    pv = sub.add_parser("serve"); pv.add_argument("--host", default="127.0.0.1"); pv.add_argument("--port", type=int, default=8765)
    pv.add_argument("--reload", action="store_true", help="kod o'zgarsa serverni qayta yuklash (dev)")
    a = p.parse_args()

    if a.cmd == "load":
        con = db.connect()
        for f in a.files:
            print(json.dumps(db.load_file(con, Path(f), exchange=a.exchange), ensure_ascii=False))
    elif a.cmd in ("demo", "loadref"):
        from app import market
        folder = Path(a.folder) if a.cmd == "loadref" else Path(__file__).parent / "data" / "demo"
        con = db.connect()
        if a.cmd == "demo":
            import runpy
            runpy.run_path(str(Path(__file__).parent / "scripts" / "make_demo_data.py"), run_name="__main__")
            print(json.dumps(db.load_file(con, folder / "DEMO_uzex_deals.csv", exchange="UZEX-DEMO"), ensure_ascii=False))
        print(json.dumps(market.load_reference(con, folder), ensure_ascii=False))
        real = Path(__file__).parent / "data" / "real"
        if a.cmd == "demo" and real.exists():  # haqiqiy kotirovkalar demo ustidan yoziladi
            print("real:", json.dumps(market.load_reference(con, real), ensure_ascii=False))
    elif a.cmd == "sync":
        from app.sources.fetch import sync
        print(json.dumps(sync(), ensure_ascii=False, indent=2))
    elif a.cmd == "info":
        print(json.dumps(db.describe(db.connect()), ensure_ascii=False, indent=2))
    elif a.cmd == "sql":
        print(db.to_frame(db.run_select(db.connect(readonly=True), a.query)).to_string(index=False))
    elif a.cmd == "ask":
        from app.agent import BirjaAgent
        r = BirjaAgent().ask(a.question)
        print(r.answer)
        if a.debug:
            print("\n--- SQL ---\n" + "\n".join(r.queries))
            print(f"verified={r.verified} unsupported={r.unsupported}")
    elif a.cmd == "chat":
        from app.agent import BirjaAgent
        agent = BirjaAgent()
        print("Savol bering (chiqish: exit)")
        while (q := input("\n> ").strip()) not in {"exit", "quit", "chiqish"}:
            if q:
                print(agent.ask(q).answer)
    elif a.cmd == "serve":
        import uvicorn
        from app import config
        if not config.DB_PATH.exists():  # birinchi ishga tushirish: DEMO ma'lumot bilan
            print("Baza topilmadi — DEMO ma'lumotlar yaratilmoqda...")
            import subprocess, sys
            subprocess.run([sys.executable, __file__, "demo"], check=True)
        port = free_port(a.host, a.port)
        if port != a.port:
            print(f"{a.port}-port band (boshqa dastur yoki allaqachon ishlayotgan server) -> {port}-port ishlatiladi")
        print(f"\n  Sayt / Site:  http://{a.host}:{port}\n")
        uvicorn.run("app.api:app", host=a.host, port=port, reload=a.reload)


if __name__ == "__main__":
    main()
