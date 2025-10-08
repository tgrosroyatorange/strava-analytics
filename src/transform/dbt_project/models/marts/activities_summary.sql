{{ config(materialized='table') }}

SELECT 
    activity_id,
    activity_name,
    sport_type,
    start_date,
    activity_date,
    activity_week,
    activity_month,
    activity_year,
    
    -- Métriques principales
    distance_km,
    moving_time_minutes,
    elapsed_time_minutes,
    total_elevation_gain_m,
    
    -- Performance
    average_speed_kmh,
    max_speed_kmh,
    pace_min_per_km,
    
    -- Cardio
    average_heartrate,
    max_heartrate,
    suffer_score,
    
    -- Calculs additionnels
    CASE 
        WHEN distance_km > 0 THEN total_elevation_gain_m / distance_km
        ELSE 0 
    END as elevation_gain_per_km,
    
    -- Catégorisation des distances
    CASE 
        WHEN distance_km < 5 THEN 'Court (< 5km)'
        WHEN distance_km < 10 THEN 'Moyen (5-10km)'
        WHEN distance_km < 21 THEN 'Long (10-21km)'
        WHEN distance_km < 42 THEN 'Très long (21-42km)'
        ELSE 'Ultra (> 42km)'
    END as distance_category,
    
    -- Catégorisation du dénivelé
    CASE 
        WHEN total_elevation_gain_m < 100 THEN 'Plat'
        WHEN total_elevation_gain_m < 300 THEN 'Vallonné'
        WHEN total_elevation_gain_m < 600 THEN 'Montagneux'
        ELSE 'Très montagneux'
    END as elevation_category

FROM {{ ref('stg_strava_activities') }}
