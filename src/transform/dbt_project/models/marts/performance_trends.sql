{{ config(materialized='table') }}

WITH monthly_performance AS (
    SELECT 
        activity_month,
        sport_type,
        
        -- Métriques de performance
        COUNT(*) as activities_count,
        ROUND(AVG(distance_km), 2) as avg_distance_km,
        ROUND(AVG(pace_min_per_km), 2) as avg_pace_min_per_km,
        ROUND(AVG(average_speed_kmh), 2) as avg_speed_kmh,
        ROUND(AVG(average_heartrate), 0) as avg_heartrate,
        
        -- Métriques de volume
        ROUND(SUM(distance_km), 1) as total_distance_km,
        ROUND(SUM(moving_time_minutes) / 60.0, 1) as total_hours,
        ROUND(SUM(total_elevation_gain_m), 0) as total_elevation_m
        
    FROM {{ ref('stg_strava_activities') }}
    WHERE activity_month >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
    GROUP BY activity_month, sport_type
),

performance_with_trends AS (
    SELECT 
        *,
        
        -- Calcul des tendances (comparaison avec le mois précédent)
        LAG(avg_pace_min_per_km) OVER (
            PARTITION BY sport_type 
            ORDER BY activity_month
        ) as prev_month_pace,
        
        LAG(total_distance_km) OVER (
            PARTITION BY sport_type 
            ORDER BY activity_month
        ) as prev_month_distance,
        
        LAG(avg_heartrate) OVER (
            PARTITION BY sport_type 
            ORDER BY activity_month
        ) as prev_month_hr
        
    FROM monthly_performance
)

SELECT 
    activity_month,
    sport_type,
    activities_count,
    avg_distance_km,
    avg_pace_min_per_km,
    avg_speed_kmh,
    avg_heartrate,
    total_distance_km,
    total_hours,
    total_elevation_m,
    
    -- Tendances (amélioration = valeurs négatives pour pace, positives pour distance)
    CASE 
        WHEN prev_month_pace IS NOT NULL 
        THEN ROUND(avg_pace_min_per_km - prev_month_pace, 2)
        ELSE NULL 
    END as pace_trend_min_per_km,
    
    CASE 
        WHEN prev_month_distance IS NOT NULL 
        THEN ROUND(total_distance_km - prev_month_distance, 1)
        ELSE NULL 
    END as distance_trend_km,
    
    CASE 
        WHEN prev_month_hr IS NOT NULL 
        THEN ROUND(avg_heartrate - prev_month_hr, 0)
        ELSE NULL 
    END as heartrate_trend_bpm

FROM performance_with_trends
ORDER BY sport_type, activity_month DESC
