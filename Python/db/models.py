import sqlite3
import os


def get_connection():
    # Vytvoření složky 'database' pokud neexistuje
    os.makedirs('database', exist_ok=True)

    # Připojení k databázi ve složce 'database'
    conn = sqlite3.connect('database/pong_game.db')
    return conn


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Tabulka hráčů
    cur.execute("""
    CREATE TABLE IF NOT EXISTS player (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Tabulka her
    cur.execute("""
    CREATE TABLE IF NOT EXISTS game (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        duration_seconds INTEGER,
        game_mode TEXT CHECK(game_mode IN ('BOT', 'PVP')) NOT NULL,
        player1_id INTEGER NOT NULL,
        player2_id INTEGER,
        winner_player_id INTEGER,
        FOREIGN KEY (player1_id) REFERENCES player(player_id),
        FOREIGN KEY (player2_id) REFERENCES player(player_id),
        FOREIGN KEY (winner_player_id) REFERENCES player(player_id)
    );
    """)

    # Tabulka skóre
    cur.execute("""
    CREATE TABLE IF NOT EXISTS score (
        score_id INTEGER PRIMARY KEY AUTOINCREMENT,
        points INTEGER NOT NULL,
        hits INTEGER DEFAULT 0,
        player_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        UNIQUE(player_id, game_id),
        FOREIGN KEY (player_id) REFERENCES player(player_id),
        FOREIGN KEY (game_id) REFERENCES game(game_id)
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Databázové tabulky vytvořeny v složce 'database'")
