import sqlite3
import os

DB_PATH = 'database/pong_game.db'


def view_database():
    if not os.path.exists(DB_PATH):
        print("❌ Databáze neexistuje! Spusť nejdřív hru.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=" * 80)
    print("🏓 VÝSLEDKY PONG")
    print("=" * 80)

    cur.execute("SELECT * FROM hry ORDER BY datum DESC")
    rows = cur.fetchall()

    if not rows:
        print("  (žádné hry)")
    else:
        print(f"\n{'Datum':<22} {'Čas(s)':<8} {'Režim':<6} {'Hráč 1':<15} {'Skóre':<8} {'Hráč 2':<15} {'Skóre':<8} {'Vítěz'}")
        print("-" * 80)
        for r in rows:
            print(f"{str(r[1]):<22} {str(r[2])+'s':<8} {r[3]:<6} {r[4]:<15} {r[5]:<8} {r[6]:<15} {r[7]:<8} {r[8]}")

    print("\n" + "=" * 80)
    conn.close()


if __name__ == "__main__":
    view_database()