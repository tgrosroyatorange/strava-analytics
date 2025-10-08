# check_transformed_data.py (version mise à jour)
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
    try:
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
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Répartition par sport
    print("\n📈 RÉPARTITION PAR SPORT:")
    try:
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
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Statistiques mensuelles récentes
    print("\n📅 STATISTIQUES MENSUELLES (3 derniers mois):")
    try:
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
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Tendances de performance
    print("\n📊 TENDANCES DE PERFORMANCE (dernier mois):")
    try:
        perf_stats = conn.execute("""
            SELECT 
                sport_type,
                activities_count,
                avg_pace_min_per_km,
                pace_trend_min_per_km,
                total_distance_km,
                distance_trend_km
            FROM performance_trends
            WHERE activity_month = (SELECT MAX(activity_month) FROM performance_trends)
        """).fetchall()
        
        for perf in perf_stats:
            trend_pace = f"({perf[3]:+.2f})" if perf[3] is not None else ""
            trend_dist = f"({perf[5]:+.1f}km)" if perf[5] is not None else ""
            print(f"  - {perf[0]}: {perf[1]} activités, pace {perf[2]} min/km {trend_pace}, {perf[4]} km {trend_dist}")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    conn.close()
    print("\n✅ Vérification terminée !")

if __name__ == "__main__":
    check_transformed_data()
