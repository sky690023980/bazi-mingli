# -*- coding: utf-8 -*-
"""
SQLite 数据库层
"""
import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from backend.config import get_settings

settings = get_settings()
DB_PATH = settings.db_path


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # 返回中文不乱码
    conn.execute("PRAGMA encoding='UTF-8'")
    return conn


@contextmanager
def get_cursor():
    conn = get_conn()
    try:
        c = conn.cursor()
        yield c
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────
# 建库脚本（幂等）
# ──────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    openid TEXT UNIQUE,
    nickname TEXT,
    avatar TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    openid TEXT,
    name TEXT,
    gender TEXT,
    year INTEGER, month INTEGER, day INTEGER, hour INTEGER,
    location TEXT,
    pillar_json TEXT,
    gua_json TEXT,
    llm_report TEXT,
    ask TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_readings_openid ON readings(openid);
CREATE INDEX IF NOT EXISTS idx_readings_created ON readings(created_at DESC);
"""


def init_db():
    """初始化数据库"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_cursor() as c:
        c.executescript(SCHEMA)
    print(f"[DB] 初始化完成 → {DB_PATH}")


# ──────────────────────────────────────
# 用户操作
# ──────────────────────────────────────
def get_or_create_user(openid: str, nickname: str = "") -> Dict:
    with get_cursor() as c:
        c.execute(
            "SELECT * FROM users WHERE openid=?",
            (openid,)
        )
        row = c.fetchone()
        if row:
            return dict(row)
        c.execute(
            "INSERT INTO users(openid,nickname) VALUES(?,?)",
            (openid, nickname)
        )
        return {"id": c.lastrowid, "openid": openid, "nickname": nickname}


# ──────────────────────────────────────
# 命盘记录
# ──────────────────────────────────────
def save_reading(
    openid: str,
    name: str, gender: str,
    year: int, month: int, day: int, hour: int,
    location: str,
    pillar_json: Dict, gua_json: Dict, llm_report: str,
    ask: str = ""
) -> int:
    with get_cursor() as c:
        c.execute("""
            INSERT INTO readings
            (openid,name,gender,year,month,day,hour,location,
             pillar_json,gua_json,llm_report,ask)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            openid, name, gender,
            year, month, day, hour, location,
            json.dumps(pillar_json, ensure_ascii=False),
            json.dumps(gua_json, ensure_ascii=False),
            llm_report, ask
        ))
        return c.lastrowid


def get_readings(openid: str, limit: int = 50) -> List[Dict]:
    with get_cursor() as c:
        rows = c.execute("""
            SELECT id, name, gender, year, month, day, hour,
                   location, pillar_json, llm_report, created_at
            FROM readings
            WHERE openid=? AND openid IS NOT NULL AND openid != ''
            ORDER BY created_at DESC
            LIMIT ?
        """, (openid, limit)).fetchall()
        return [dict(r) for r in rows]


def get_reading_by_id(reading_id: int) -> Optional[Dict]:
    with get_cursor() as c:
        row = c.execute(
            "SELECT * FROM readings WHERE id=?",
            (reading_id,)
        ).fetchone()
        return dict(row) if row else None


def get_recent_readings(limit: int = 20) -> List[Dict]:
    """获取最近记录（不绑定用户）"""
    with get_cursor() as c:
        rows = c.execute("""
            SELECT id, name, gender, year, month, day, hour,
                   location, pillar_json, created_at
            FROM readings
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
