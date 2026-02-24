import sqlite3
import os
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'pong_game.db')

CAS_ZONA = timezone(timedelta(hours=1))  # Zimní čas (UTC+1)


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def get_now():
    return datetime.now(CAS_ZONA).strftime('%Y-%m-%d %H:%M:%S')


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Jen vytvoří tabulku pokud ještě neexistuje - NEMAŽE data
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hry (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        datum        TEXT,
        delka_sekund INTEGER,
        rezim        TEXT,
        hrac1        TEXT,
        skore1       INTEGER,
        hrac2        TEXT,
        skore2       INTEGER,
        vítez        TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Databáze připravena")