import os
import requests
import json
import duckdb
from datetime import datetime
import time
import sys

def get_strava_credentials():
    """Récupère les credentials Strava (local ou cloud)"""
    
    # Essayer d'abord Streamlit secrets (cloud) - seulement si streamlit est disponible
    try:
        import streamlit as st
        # Vérifier que nous sommes dans un contexte Streamlit ET que les secrets existent
        if hasattr(st, 'secrets') and 'strava' in st.secrets:
            print("🌐 Utilisation des secrets Streamlit Cloud")
            return {
                'client_id': st.secrets['strava']['client_id'],
                'client_secret': st.secrets['strava']['client_secret'],
                'refresh_token': st.secrets['strava']['refresh_token']
            }
    except (ImportError, AttributeError, KeyError) as e:
        # Streamlit non disponible ou secrets non configurés
        print(f"ℹ️ Streamlit secrets non disponibles: {e}")
        pass
    
    # Fallback vers variables d'environnement (local)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("🏠 Chargement du fichier .env")
    except ImportError:
        print("⚠️ python-dotenv non disponible, utilisation des variables d'environnement système")
    
    # Récupérer depuis les variables d'environnement
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
    
    # Vérifier que les credentials sont présents
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "❌ Credentials Strava manquants. Vérifiez :\n"
            "- Fichier .env avec : STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN\n"
            "- Ou secrets Streamlit Cloud configurés"
        )
    
    print("✅ Credentials Strava chargés avec succès")
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }

class StravaExtractor:
    def __init__(self):
        """Initialise l'extracteur avec les credentials"""
        try:
            credentials = get_strava_credentials()
            self.client_id = credentials['client_id']
            self.client_secret = credentials['client_secret']
            self.refresh_token = credentials['refresh_token']
            print("✅ StravaExtractor initialisé avec succès")
        except Exception as e:
            print(f"❌ Erreur lors du chargement des credentials: {e}")
            raise
        
        self.access_token = None
        self.base_url = "https://www.strava.com/api/v3"
        self.db_path = 'data/strava.duckdb'
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs('data', exist_ok=True)
        
    def get_latest_activity_date(self):
        """Récupère la date de la dernière activité en base"""
        try:
            if not os.path.exists(self.db_path):
                print("Base de donnees inexistante, extraction complete")
                return None
            
            conn = duckdb.connect(self.db_path)
            
            # Vérifier si la table existe
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
            
            if 'raw_activities' not in table_names:
                print("Table raw_activities inexistante, extraction complete")
                conn.close()
                return None
            
            # Récupérer la date de la dernière activité
            result = conn.execute("""
                SELECT MAX(start_date) as latest_date, COUNT(*) as total_count
                FROM raw_activities
            """).fetchone()
            
            conn.close()
            
            if result and result[0]:
                latest_date = result[0]
                total_count = result[1]
                print(f"Derniere activite en base: {latest_date}")
                print(f"Total activites en base: {total_count}")
                return latest_date
            else:
                print("Aucune activite en base, extraction complete")
                return None
                
        except Exception as e:
            print(f"Erreur lors de la verification de la base: {e}")
            return None
    
    def get_existing_activity_ids(self):
        """Récupère les IDs des activités déjà en base"""
        try:
            if not os.path.exists(self.db_path):
                return set()
            
            conn = duckdb.connect(self.db_path)
            
            # Vérifier si la table existe
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
            
            if 'raw_activities' not in table_names:
                conn.close()
                return set()
            
            # Récupérer tous les IDs existants
            result = conn.execute("SELECT id FROM raw_activities").fetchall()
            conn.close()
            
            existing_ids = {row[0] for row in result}
            print(f"IDs existants en base: {len(existing_ids)}")
            return existing_ids
            
        except Exception as e:
            print(f"Erreur lors de la recuperation des IDs: {e}")
            return set()
    
    def refresh_access_token(self):
        """Rafraîchit le token d'accès"""
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print("Token rafraichi avec succes")
                return True
            else:
                print(f"Erreur lors du rafraichissement : {response.status_code}")
                print(f"Reponse : {response.text}")
                return False
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            return False
    
    def get_activities(self, per_page=80, incremental=True):
        """Récupère les activités depuis Strava (mode incrémental par défaut)"""
        if not self.refresh_access_token():
            return None
        
        # Récupérer les IDs existants pour comparaison
        existing_ids = self.get_existing_activity_ids() if incremental else set()
        
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'per_page': per_page}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                all_activities = response.json()
                print(f"{len(all_activities)} activites recuperees depuis Strava")
                
                if incremental and existing_ids:
                    # Filtrer les nouvelles activités
                    new_activities = [
                        activity for activity in all_activities 
                        if activity['id'] not in existing_ids
                    ]
                    
                    print(f"{len(new_activities)} nouvelles activites detectees")
                    
                    if len(new_activities) == 0:
                        print("Aucune nouvelle activite - Arret du processus")
                        return []  # Retourner une liste vide pour indiquer "pas de nouvelles données"
                    
                    return new_activities
                else:
                    # Mode complet ou première extraction
                    return all_activities
                    
            else:
                print(f"Erreur API : {response.status_code}")
                print(f"Reponse : {response.text}")
                return None
        except Exception as e:
            print(f"Erreur lors de la recuperation : {e}")
            return None
    
    def init_database(self):
        """Initialise la base de données avec une nouvelle connexion propre"""
        try:
            # Supprimer le fichier s'il existe et est corrompu
            if os.path.exists(self.db_path):
                try:
                    # Test de connexion
                    test_conn = duckdb.connect(self.db_path)
                    test_conn.execute("SELECT 1").fetchone()
                    test_conn.close()
                    print("Base de donnees existante OK")
                    return True
                except:
                    print("Base de donnees corrompue, suppression...")
                    os.remove(self.db_path)
                    if os.path.exists(self.db_path + '.wal'):
                        os.remove(self.db_path + '.wal')
            
            # Créer une nouvelle base
            conn = duckdb.connect(self.db_path)
            
            # Créer la table
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
            
            conn.close()
            print("Base de donnees initialisee")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation : {e}")
            return False
    
    def save_to_duckdb(self, activities):
        """Sauvegarde les activités dans DuckDB"""
        if not activities:
            print("Aucune activite a sauvegarder")
            return False
        
        if len(activities) == 0:
            print("Liste d'activites vide")
            return True  # Pas d'erreur, juste rien à faire
            
        try:
            # Initialiser la base si nécessaire
            if not self.init_database():
                return False
            
            # Connexion à DuckDB
            conn = duckdb.connect(self.db_path)
            
            # Insérer les données une par une pour éviter les erreurs
            success_count = 0
            error_count = 0
            
            for activity in activities:
                try:
                    # Nettoyer les données avant insertion
                    activity_data = {
                        'id': activity.get('id'),
                        'name': str(activity.get('name', '')).replace('\x00', '').encode('utf-8', 'ignore').decode('utf-8'),
                        'sport_type': activity.get('sport_type'),
                        'start_date': activity.get('start_date_local'),
                        'distance': activity.get('distance'),
                        'moving_time': activity.get('moving_time'),
                        'elapsed_time': activity.get('elapsed_time'),
                        'total_elevation_gain': activity.get('total_elevation_gain'),
                        'average_speed': activity.get('average_speed'),
                        'max_speed': activity.get('max_speed'),
                        'average_heartrate': activity.get('average_heartrate'),
                        'max_heartrate': activity.get('max_heartrate'),
                        'suffer_score': activity.get('suffer_score')
                    }
                    
                    # Nettoyer le JSON aussi
                    clean_activity = {}
                    for key, value in activity.items():
                        if isinstance(value, str):
                            clean_value = value.replace('\x00', '').encode('utf-8', 'ignore').decode('utf-8')
                            clean_activity[key] = clean_value
                        else:
                            clean_activity[key] = value
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO raw_activities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        activity_data['id'],
                        activity_data['name'],
                        activity_data['sport_type'],
                        activity_data['start_date'],
                        activity_data['distance'],
                        activity_data['moving_time'],
                        activity_data['elapsed_time'],
                        activity_data['total_elevation_gain'],
                        activity_data['average_speed'],
                        activity_data['max_speed'],
                        activity_data['average_heartrate'],
                        activity_data['max_heartrate'],
                        activity_data['suffer_score'],
                        json.dumps(clean_activity, ensure_ascii=True)
                    ))
                    success_count += 1
                    
                except Exception as e:
                    print(f"Erreur pour l'activite {activity.get('id', 'unknown')}: {e}")
                    error_count += 1
                    continue
            
            conn.close()
            print(f"{success_count} nouvelles activites sauvegardees avec succes")
            if error_count > 0:
                print(f"{error_count} activites ont echoue")
            
            return success_count > 0
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False

def main():
    """Fonction principale"""
    print("🚀 Extraction des donnees Strava...")
    
    try:
        # ✅ CORRECTION : Créer l'extracteur qui va gérer le chargement des credentials
        extractor = StravaExtractor()
        
        # Extraction incrémentale par défaut
        activities = extractor.get_activities(incremental=True)
        
        if activities is None:
            print("❌ Echec de l'extraction")
            sys.exit(1)
        elif len(activities) == 0:
            print("✅ Aucune nouvelle activite - Processus termine")
            sys.exit(0)  # Code 0 = succès mais rien à faire
        else:
            if extractor.save_to_duckdb(activities):
                print("🎉 Extraction terminee avec succes !")
                sys.exit(0)
            else:
                print("❌ Echec de la sauvegarde")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
