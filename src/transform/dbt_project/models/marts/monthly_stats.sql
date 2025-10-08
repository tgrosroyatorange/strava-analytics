{{ config(materialized='table') }}

SELECT 
    activity_month,
    EXTRACT(YEAR FROM activity_month) as year,
    EXTRACT(MONTH FROM activity_month) as month,
    
    -- Compteurs
    COUNT(*) as total_activities,
    COUNT(CASE WHEN sport_type = 'Run' THEN 1 END) as road_runs,
    COUNT(CASE WHEN sport_type = 'Trail Run' THEN 1 END) as trail_runs,
    
    -- Distance
    ROUND(SUM(distance_km), 1) as total_distance_km,
    ROUND(AVG(distance_km), 1) as avg_distance_km,
    ROUND(MAX(distance_km), 1) as max_distance_km,
    
    -- Temps
    ROUND(SUM(moving_time_minutes), 0) as total_moving_time_minutes,
    ROUND(SUM(moving_time_minutes) / 60.0, 1) as total_moving_time_hours,
    ROUND(AVG(moving_time_minutes), 1) as avg_moving_time_minutes,
    
    -- Dénivelé
    ROUND(SUM(total_elevation_gain_m), 0) as total_elevation_gain_m,
    ROUND(AVG(total_elevation_gain_m), 0) as avg_elevation_gain_m,
    
    -- Performance
    ROUND(AVG(average_speed_kmh), 2) as avg_speed_kmh,
    ROUND(AVG(pace_min_per_km), 2) as avg_pace_min_per_km,
    
    -- Cardio (si disponible)
    ROUND(AVG(average_heartrate), 0) as avg_heartrate,
    ROUND(AVG(max_heartrate), 0) as avg_max_heartrate,
    
    -- Fréquence
    ROUND(COUNT(*) / 4.33, 1) as activities_per_week  -- Approximation

FROM {{ ref('stg_strava_activities') }}
GROUP BY activity_month
ORDER BY activity_month DESC