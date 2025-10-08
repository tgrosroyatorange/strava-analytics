import duckdb

def check_transformed_data():
    conn = duckdb.connect('data/strava.duckdb')
    
    print("=== VÉRIFICATION DES DONNÉES TRANSFORMÉES ===\n")
    
    # Vérifier les tables créées
    tables = conn.execute("SHOW TABLES").fetchall()
    print("📊 Tables disponibles :")
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
        print(f"  - {table[0]}: {count} lignes")
    
    print("\n" + "="*50)
    
    # Statistiques du staging
    print("\n🏃‍♂️ DONNÉES STAGING (stg_strava_activities):")
    staging_stats = conn.execute("""
        SELECT 
            COUNT(*) as total_activities,
            ROUND(SUM(distance_km), 1) as total_distance_km,
            ROUND(AVG(distance_km), 1) as avg_distance_km,
            MIN(activity_date) as first_activity,
            MAX(activity_date) as last_activity
        FROM stg_strava_activities
    """).fetchone()
    
    print(f"  Total activités: {staging_stats[0]}")
    print(f"  Distance totale: {staging_stats[1]} km")
    print(f"  Distance moyenne: {staging_stats[2]} km")
    print(f"  Première activité: {staging_stats[3]}")
    print(f"  Dernière activité: {staging_stats[4]}")
    
    # Répartition par sport
    print("\n📈 RÉPARTITION PAR SPORT:")
    sport_stats = conn.execute("""
        SELECT 
            sport_type,
            COUNT(*) as count,
            ROUND(SUM(distance_km), 1) as total_km
        FROM stg_strava_activities
        GROUP BY sport_type
        ORDER BY count DESC
    """).fetchall()
    
    for sport in sport_stats:
        print(f"  - {sport[0]}: {sport[1]} activités, {sport[2]} km")
    
    # Statistiques mensuelles récentes
    print("\n📅 STATISTIQUES MENSUELLES (3 derniers mois):")
    monthly_stats = conn.execute("""
        SELECT 
            activity_month,
            total_activities,
            total_distance_km,
            avg_distance_km,
            total_moving_time_hours
        FROM monthly_stats
        ORDER BY activity_month DESC
        LIMIT 3
    """).fetchall()
    
    for month in monthly_stats:
        print(f"  - {month[0]}: {month[1]} activités, {month[2]} km, {month[4]}h")
    
    conn.close()
    print("\n✅ Vérification terminée !")

if __name__ == "__main__":
    check_transformed_data()
