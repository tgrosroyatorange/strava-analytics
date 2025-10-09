{{ config(materialized='view') }}

WITH cleaned_activities AS (
    SELECT 
        id as activity_id,
        name as activity_name,
        sport_type,
        CAST(start_date AS TIMESTAMP) as start_date,
        
        -- Conversions d'unités
        ROUND(distance / 1000.0, 2) as distance_km,
        ROUND(moving_time / 60.0, 1) as moving_time_minutes,
        ROUND(elapsed_time / 60.0, 1) as elapsed_time_minutes,
        COALESCE(total_elevation_gain, 0) as total_elevation_gain_m,
        
        -- Vitesses (conversion m/s vers km/h)
        CASE 
            WHEN average_speed > 0 THEN ROUND(average_speed * 3.6, 2)
            ELSE NULL 
        END as average_speed_kmh,
        
        CASE 
            WHEN max_speed > 0 THEN ROUND(max_speed * 3.6, 2)
            ELSE NULL 
        END as max_speed_kmh,
        
        -- Fréquence cardiaque
        ROUND(average_heartrate, 0) as average_heartrate,
        ROUND(max_heartrate, 0) as max_heartrate,
        
        -- Autres métriques
        COALESCE(suffer_score, 0) as suffer_score,
        
        -- Calcul de l'allure au format MM.SS (4:30 = 4.30)
        CASE 
            WHEN CAST(distance AS FLOAT) > 0 AND CAST(moving_time AS INTEGER) > 0 THEN
                -- Calcul des secondes par km
                CASE 
                    WHEN (CAST(moving_time AS INTEGER) / (CAST(distance AS FLOAT) / 1000)) IS NOT NULL THEN
                        -- Minutes + (secondes / 100) pour avoir le format MM.SS
                        FLOOR((CAST(moving_time AS INTEGER) / (CAST(distance AS FLOAT) / 1000)) / 60) + 
                        (((CAST(moving_time AS INTEGER) / (CAST(distance AS FLOAT) / 1000)) % 60) / 100.0)
                    ELSE NULL
                END
            ELSE NULL 
        END as pace_min_per_km,
        
        -- Dates pour agrégations
        DATE_TRUNC('day', CAST(start_date AS TIMESTAMP)) as activity_date,
        DATE_TRUNC('week', CAST(start_date AS TIMESTAMP)) as activity_week,
        DATE_TRUNC('month', CAST(start_date AS TIMESTAMP)) as activity_month,
        DATE_TRUNC('year', CAST(start_date AS TIMESTAMP)) as activity_year,
        
        -- Métadonnées
        updated_at
        
    FROM {{ source('raw_strava', 'raw_activities') }}
    --FROM main.raw_activities 
    WHERE (lower(sport_type) like '%run%' or lower(sport_type) like '%trail%')
      AND distance > 0  -- Exclure les activités sans distance
      AND moving_time > 0  -- Exclure les activités sans temps
)

SELECT * FROM cleaned_activities
