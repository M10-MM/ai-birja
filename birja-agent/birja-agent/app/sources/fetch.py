"""sources.json dagi manbalarni yuklab olib, data/raw ga saqlaydi va bazaga yuklaydi.

Har bir manba — birja rasmiy saytida e'lon qilingan fayl yoki jadvalli sahifa havolasi
(CSV, XLSX, JSON yoki HTML jadval). Havolalarni o'zingiz rasmiy saytdan olib qo'yasiz:
loyiha hech qanday ma'lumotni o'ylab topmaydi.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from .. import config, db

UA = "birja-agent/0.1 (+open-data loader)"


def load_sources(path: Path | None = None) -> list[dict]:
    path = Path(path or config.SOURCES_FILE)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [s for s in data.get("sources", []) if s.get("enabled", True) and s.get("url")]


def download(url: str, dest_dir: Path, name: str | None = None) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = name or Path(urlparse(url).path).name or "page.html"
    if "." not in fname:
        fname += ".html"
    dest = dest_dir / fname
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())
    return dest


def sync(sources_file: Path | None = None) -> list[dict]:
    con = db.connect()
    report = []
    for s in load_sources(sources_file):
        try:
            f = download(s["url"], config.RAW_DIR, s.get("filename"))
            r = db.load_file(con, f, exchange=s.get("exchange"), url=s["url"])
            report.append({"source": s.get("name", s["url"]), **r})
        except Exception as e:
            report.append({"source": s.get("name", s["url"]), "error": str(e)})
    return report
