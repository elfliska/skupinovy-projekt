import sqlite3
import os

DB_PATH = 'database/pong_game.db'


def view_database():
    if not os.path.exists(DB_PATH):
        print("❌ Databáze neexistuje! Spusť nejdřív hru.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=" * 95)
    print("🏓 VÝSLEDKY PONG")
    print("=" * 95)

    cur.execute("""
        SELECT
            g.game_id,
            g.played_at,
            g.duration_seconds,
            g.game_mode,
            p1.username        AS hrac1,
            s1.points          AS skore1,
            s1.hits            AS hity1,
            p2.username        AS hrac2,
            s2.points          AS skore2,
            COALESCE(pw.username, 'Remíza') AS vítez
        FROM game g
        JOIN player  p1 ON p1.player_id = g.player1_id
        JOIN player  p2 ON p2.player_id = g.player2_id
        JOIN score   s1 ON s1.game_id   = g.game_id AND s1.player_id = g.player1_id
        JOIN score   s2 ON s2.game_id   = g.game_id AND s2.player_id = g.player2_id
        LEFT JOIN player pw ON pw.player_id = g.winner_player
        ORDER BY g.played_at DESC
    """)
    rows = cur.fetchall()

    if not rows:
        print("  (žádné hry)")
    else:
        print(f"\n{'#':<5} {'Datum':<22} {'Čas(s)':<8} {'Režim':<6} "
              f"{'Hráč 1':<15} {'Skóre':<7} {'Hity':<6} "
              f"{'Hráč 2':<15} {'Skóre':<7} {'Vítěz'}")
        print("-" * 95)
        for r in rows:
            print(f"{r[0]:<5} {str(r[1]):<22} {str(r[2])+'s':<8} {r[3]:<6} "
                  f"{r[4]:<15} {r[5]:<7} {r[6]:<6} "
                  f"{r[7]:<15} {r[8]:<7} {r[9]}")

    print("\n" + "=" * 95)
    conn.close()


if __name__ == "__main__":
    view_database()
