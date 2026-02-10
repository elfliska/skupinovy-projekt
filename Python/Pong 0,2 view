import sqlite3
import os


def view_database():
    """Zobrazí celý obsah databáze"""

    db_path = 'database/pong_game.db'

    # Kontrola existence databáze
    if not os.path.exists(db_path):
        print("❌ Databáze ještě neexistuje!")
        print("💡 Spusť nejdřív hru, aby se databáze vytvořila.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("=" * 70)
    print("📊 OBSAH DATABÁZE PONG")
    print("=" * 70)

    # ===== TABULKA PLAYER =====
    print("\n🎮 HRÁČI:")
    print("-" * 70)
    cur.execute("SELECT * FROM player")
    players = cur.fetchall()

    if players:
        print(f"{'ID':<5} {'Jméno':<20} {'Vytvořeno':<25}")
        print("-" * 70)
        for player in players:
            print(f"{player[0]:<5} {player[1]:<20} {player[2]:<25}")
    else:
        print("  (žádní hráči)")

    # ===== TABULKA GAME =====
    print("\n\n🕹️  HRY:")
    print("-" * 70)
    cur.execute("""
        SELECT 
            g.game_id,
            g.played_at,
            g.duration_seconds,
            g.game_mode,
            p1.username as player1,
            p2.username as player2,
            pw.username as winner
        FROM game g
        LEFT JOIN player p1 ON g.player1_id = p1.player_id
        LEFT JOIN player p2 ON g.player2_id = p2.player_id
        LEFT JOIN player pw ON g.winner_player_id = pw.player_id
    """)
    games = cur.fetchall()

    if games:
        print(f"{'ID':<5} {'Datum':<20} {'Trvání(s)':<10} {'Režim':<8} {'Hráč 1':<15} {'Hráč 2':<15} {'Vítěz':<15}")
        print("-" * 70)
        for game in games:
            p2 = game[5] if game[5] else "BOT"
            winner = game[6] if game[6] else "-"
            print(f"{game[0]:<5} {game[1]:<20} {game[2]:<10} {game[3]:<8} {game[4]:<15} {p2:<15} {winner:<15}")
    else:
        print("  (žádné hry)")

    # ===== TABULKA SCORE =====
    print("\n\n📈 SKÓRE:")
    print("-" * 70)
    cur.execute("""
        SELECT 
            s.score_id,
            p.username,
            s.points,
            s.hits,
            g.game_id,
            g.game_mode
        FROM score s
        JOIN player p ON s.player_id = p.player_id
        JOIN game g ON s.game_id = g.game_id
        ORDER BY s.score_id DESC
    """)
    scores = cur.fetchall()

    if scores:
        print(f"{'ID':<5} {'Hráč':<20} {'Body':<8} {'Hity':<8} {'Hra ID':<10} {'Režim':<8}")
        print("-" * 70)
        for score in scores:
            print(f"{score[0]:<5} {score[1]:<20} {score[2]:<8} {score[3]:<8} {score[4]:<10} {score[5]:<8}")
    else:
        print("  (žádné skóre)")

    # ===== STATISTIKY =====
    print("\n\n📊 STATISTIKY:")
    print("-" * 70)

    # Nejlepší hráč podle bodů
    cur.execute("""
        SELECT p.username, SUM(s.points) as total_points, COUNT(s.score_id) as games_played
        FROM player p
        JOIN score s ON p.player_id = s.player_id
        GROUP BY p.player_id
        ORDER BY total_points DESC
        LIMIT 5
    """)
    top_players = cur.fetchall()

    if top_players:
        print("\n🏆 TOP 5 HRÁČŮ (celkové body):")
        for i, (username, points, games) in enumerate(top_players, 1):
            print(f"  {i}. {username}: {points} bodů ({games} her)")

    # Průměrné skóre
    cur.execute("SELECT AVG(points) FROM score")
    avg_score = cur.fetchone()[0]
    if avg_score:
        print(f"\n📊 Průměrné skóre: {avg_score:.2f} bodů")

    # Celkový počet her
    cur.execute("SELECT COUNT(*) FROM game")
    total_games = cur.fetchone()[0]
    print(f"🎮 Celkem odehráno her: {total_games}")

    print("\n" + "=" * 70)

    conn.close()


if __name__ == "__main__":
    view_database()
