import os
import sys
import duckdb
import pandas as pd

def debug_dashboard():
    """Débogue les problèmes du dashboard"""
    
    print("🔍 DIAGNOSTIC DU DASHBOARD")
    print("=" * 40)
    
    # 1. Vérifier les fichiers
    files_to_check = [
        'src/dashboard/streamlit_app.py',
        'data/strava.duckdb',
        '.env'
    ]
    
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        print(f"📁 {file_path}: {'✅' if exists else '❌'}")
    
    # 2. Vérifier les packages
    packages = ['streamlit', 'duckdb', 'plotly', 'pandas']
    for package in packages:
        try:
            __import__(package)
            print(f"📦 {package}: ✅")
        except ImportError:
            print(f"📦 {package}: ❌ (pip install {package})")
    
    # 3. Vérifier la base de données
    if os.path.exists('data/strava.duckdb'):
        try:
            conn = duckdb.connect('data/strava.duckdb')
            tables = conn.execute("SHOW TABLES").fetchall()
            
            print(f"\n💾 Tables dans la DB:")
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                print(f"  - {table[0]}: {count} lignes")
            
            # Test de chargement des données principales
            required_tables = ['activities_summary', 'monthly_stats']
            for table in required_tables:
                try:
                    df = conn.execute(f"SELECT * FROM {table} LIMIT 1").df()
                    print(f"✅ {table}: OK")
                except Exception as e:
                    print(f"❌ {table}: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erreur DB: {e}")
    
    # 4. Test du chemin relatif
    dashboard_path = 'src/dashboard/streamlit_app.py'
    if os.path.exists(dashboard_path):
        # Simuler le chemin depuis le dashboard vers la DB
        os.chdir('src/dashboard')
        db_relative_path = '../../data/strava.duckdb'
        db_exists_from_dashboard = os.path.exists(db_relative_path)
        print(f"🔗 Chemin relatif DB depuis dashboard: {'✅' if db_exists_from_dashboard else '❌'}")
        os.chdir('../..')  # Retour à la racine
    
    print("\n" + "=" * 40)
    print("🚀 Pour lancer le dashboard :")
    print("   python run_dashboard.py")
    print("   ou")
    print("   streamlit run src/dashboard/streamlit_app.py")

if __name__ == "__main__":
    debug_dashboard()
