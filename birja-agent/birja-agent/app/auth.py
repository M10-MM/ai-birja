"""Shaxsiy kabinet: ro'yxatdan o'tish, kirish, kuzatuv ro'yxati, savollar tarixi.

Alohida `users.db` — bitimlar bazasi agent uchun faqat o'qish rejimida qoladi.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from pathlib import Path

from . import config

USERS_DB = Path(os.getenv("BIRJA_USERS_DB", config.ROOT / "data" / "users.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY, login TEXT UNIQUE NOT NULL, name TEXT, role TEXT,
  salt TEXT NOT NULL, pw TEXT NOT NULL, lang TEXT DEFAULT 'ru', created TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER, created TEXT DEFAULT (datetime('now')));
CREATE TABLE IF NOT EXISTS watchlist (user_id INTEGER, kind TEXT, code TEXT, PRIMARY KEY (user_id, kind, code));
CREATE TABLE IF NOT EXISTS history (
  id INTEGER PRIMARY KEY, user_id INTEGER, question TEXT, answer TEXT, verified INTEGER,
  queries TEXT, created TEXT DEFAULT (datetime('now'))
);
"""

ROLES = {"investor", "broker", "participant"}


class AuthError(ValueError):
    pass


def connect() -> sqlite3.Connection:
    USERS_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(USERS_DB, check_same_thread=False, timeout=10)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def _hash(pw: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()


def _session(con, uid: int) -> str:
    token = secrets.token_urlsafe(32)
    con.execute("INSERT INTO sessions(token, user_id) VALUES (?,?)", (token, uid))
    con.commit()
    return token


def register(con, login: str, password: str, name: str = "", role: str = "investor") -> dict:
    login = login.strip().lower()
    if len(login) < 3 or len(password) < 6:
        raise AuthError("short")
    if role not in ROLES:
        role = "investor"
    salt = secrets.token_hex(16)
    try:
        cur = con.execute("INSERT INTO users(login, name, role, salt, pw) VALUES (?,?,?,?,?)",
                          (login, name.strip() or login, role, salt, _hash(password, salt)))
    except sqlite3.IntegrityError:
        con.rollback()
        raise AuthError("exists")
    return {"token": _session(con, cur.lastrowid), "user": me(con, cur.lastrowid)}


def login(con, login: str, password: str, role: str | None = None) -> dict:
    u = con.execute("SELECT * FROM users WHERE login=?", (login.strip().lower(),)).fetchone()
    if not u or not hmac.compare_digest(u["pw"], _hash(password, u["salt"])):
        raise AuthError("invalid")
    return {"token": _session(con, u["id"]), "user": me(con, u["id"])}


def user_id(con, token: str | None) -> int | None:
    if not token:
        return None
    r = con.execute("SELECT user_id FROM sessions WHERE token=?", (token,)).fetchone()
    return r[0] if r else None


def logout(con, token: str) -> None:
    con.execute("DELETE FROM sessions WHERE token=?", (token,))
    con.commit()


def me(con, uid: int) -> dict:
    u = con.execute("SELECT id, login, name, role, lang, created FROM users WHERE id=?", (uid,)).fetchone()
    return dict(u) if u else {}


def watchlist(con, uid: int) -> list[dict]:
    return [dict(r) for r in con.execute("SELECT kind, code FROM watchlist WHERE user_id=?", (uid,))]


def toggle_watch(con, uid: int, kind: str, code: str) -> list[dict]:
    if con.execute("DELETE FROM watchlist WHERE user_id=? AND kind=? AND code=?", (uid, kind, code)).rowcount == 0:
        con.execute("INSERT INTO watchlist VALUES (?,?,?)", (uid, kind, code))
    con.commit()
    return watchlist(con, uid)


def add_history(con, uid: int, question: str, answer: str, verified: bool, queries: list[str]) -> None:
    con.execute("INSERT INTO history(user_id, question, answer, verified, queries) VALUES (?,?,?,?,?)",
                (uid, question, answer, int(verified), json.dumps(queries, ensure_ascii=False)))
    con.commit()


def history(con, uid: int, limit: int = 50) -> list[dict]:
    rows = con.execute("SELECT id, question, answer, verified, queries, created FROM history WHERE user_id=? "
                       "ORDER BY id DESC LIMIT ?", (uid, limit)).fetchall()
    return [{**dict(r), "queries": json.loads(r["queries"] or "[]")} for r in rows]
