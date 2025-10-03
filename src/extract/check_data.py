import duckdb

# Connexion à la base
conn = duckdb.connect('data/strava.duckdb')

# Vérifier les données
print("=== VÉRIFICATION DES DONNÉES ===")
print(f"Nombre d'activités : {conn.execute('SELECT COUNT(*) FROM raw_activities').fetchone()[0]}")
print("\nDernières activités :")
result = conn.execute("""
    SELECT name, sport_type, start_date, distance/1000 as distance_km 
    FROM raw_activities 
    ORDER BY start_date DESC 
    LIMIT 5
""").fetchall()

for row in result:
    print(f"- {row[0]} ({row[1]}) - {row[2]} - {row[3]:.1f}km")

conn.close()
