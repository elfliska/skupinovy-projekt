import sqlite3
import os
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'pong_game.db')

CAS_ZONA = timezone(timedelta(hours=1))  # Zimní čas (UTC+1)


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_now():
    return datetime.now(CAS_ZONA).strftime('%Y-%m-%d %H:%M:%S')


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS player (
        player_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        username   TEXT    UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS game (
        game_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        played_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
        duration_seconds INTEGER,
        game_mode        TEXT    NOT NULL,
        player1_id       INTEGER NOT NULL REFERENCES player(player_id),
        player2_id       INTEGER          REFERENCES player(player_id),
        winner_player    INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS score (
        score_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        points    INTEGER NOT NULL,
        hits      INTEGER DEFAULT 0,
        player_id INTEGER NOT NULL REFERENCES player(player_id),
        game_id   INTEGER NOT NULL REFERENCES game(game_id),
        UNIQUE (player_id, game_id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Databáze připravena")


def get_or_create_player(cur, username):
    """Vrátí player_id pro dané jméno, případně hráče vytvoří."""
    cur.execute("SELECT player_id FROM player WHERE username = ?", (username,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO player (username) VALUES (?)", (username,))
    return cur.lastrowid