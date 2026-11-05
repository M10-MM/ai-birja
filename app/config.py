"""Sozlamalar: .env yoki muhit o'zgaruvchilaridan o'qiladi."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

DB_PATH = Path(os.getenv("BIRJA_DB_PATH", ROOT / "data" / "birja.db"))
RAW_DIR = Path(os.getenv("BIRJA_RAW_DIR", ROOT / "data" / "raw"))
SOURCES_FILE = Path(os.getenv("BIRJA_SOURCES_FILE", ROOT / "sources.json"))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("BIRJA_MODEL", "claude-sonnet-5-5")
MAX_TOOL_ROUNDS = int(os.getenv("BIRJA_MAX_TOOL_ROUNDS", "8"))
MAX_ROWS = int(os.getenv("BIRJA_MAX_ROWS", "200"))
