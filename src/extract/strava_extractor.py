import requests
import duckdb
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class StravaExtractor:
    def __init__(self):
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        self.access_token = None
        
    def refresh_access_token(self):
        """Rafraîchit le token d'accès"""
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            print("✅ Token rafraîchi avec succès")
            return True
        else:
            print(f"❌ Erreur lors du rafraîchissement : {response.status_code}")
            return False
    
    def get_activities(self, per_page=100):
        """Récupère les activités depuis Strava"""
        if not self.refresh_access_token():
            return None
            
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'per_page': per_page}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            activities = response.json()
            print(f"✅ {len(activities)} activités récupérées")
            return activities
        else:
            print(f"❌ Erreur API : {response.status_code}")
            return None
    
    def save_to_duckdb(self, activities):
        """Sauvegarde les activités dans DuckDB"""
        if not activities:
            return
            
        # Connexion à DuckDB
        conn = duckdb.connect('data/strava.duckdb')
        
        # Créer la table si elle n'existe pas
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_activities (
                id BIGINT PRIMARY KEY,
                name VARCHAR,
                sport_type VARCHAR,
                start_date TIMESTAMP,
                distance FLOAT,
                moving_time INTEGER,
                elapsed_time INTEGER,
                total_elevation_gain FLOAT,
                average_speed FLOAT,
                max_speed FLOAT,
                average_heartrate FLOAT,
                max_heartrate FLOAT,
                suffer_score INTEGER,
                raw_data JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insérer les données
        for activity in activities:
            conn.execute("""
                INSERT OR REPLACE INTO raw_activities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                activity.get('id'),
                activity.get('name'),
                activity.get('sport_type'),
                activity.get('start_date'),
                activity.get('distance'),
                activity.get('moving_time'),
                activity.get('elapsed_time'),
                activity.get('total_elevation_gain'),
                activity.get('average_speed'),
                activity.get('max_speed'),
                activity.get('average_heartrate'),
                activity.get('max_heartrate'),
                activity.get('suffer_score'),
                json.dumps(activity)
            ))
        
        conn.close()
        print(f"✅ {len(activities)} activités sauvegardées dans DuckDB")

def main():
    """Fonction principale"""
    print("🏃‍♂️ Extraction des données Strava...")
    
    extractor = StravaExtractor()
    activities = extractor.get_activities()
    
    if activities:
        extractor.save_to_duckdb(activities)
        print("✅ Extraction terminée avec succès !")
    else:
        print("❌ Échec de l'extraction")

if __name__ == "__main__":
    main()
