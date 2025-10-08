import os
import sys
from dotenv import load_dotenv

def diagnose_environment():
    print("🔍 DIAGNOSTIC DE L'ENVIRONNEMENT")
    print("=" * 40)
    
    # Python
    print(f"Python version: {sys.version}")
    
    # Variables d'environnement
    load_dotenv()
    print(f"\n📁 Fichier .env existe: {os.path.exists('.env')}")
    
    required_vars = ['STRAVA_CLIENT_ID', 'STRAVA_CLIENT_SECRET', 'STRAVA_REFRESH_TOKEN']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value[:4])}...")
        else:
            print(f"❌ {var}: MANQUANT")
    
    # Dossiers
    print(f"\n📂 Dossier data existe: {os.path.exists('data')}")
    print(f"📂 Dossier src existe: {os.path.exists('src')}")
    
    # Fichiers
    db_path = 'data/strava.duckdb'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"💾 Base DuckDB: {size} bytes")
    else:
        print("💾 Base DuckDB: N'existe pas")
    
    # Test d'import
    try:
        import duckdb
        print(f"✅ DuckDB: {duckdb.__version__}")
    except ImportError as e:
        print(f"❌ DuckDB: {e}")
    
    try:
        import requests
        print(f"✅ Requests: {requests.__version__}")
    except ImportError as e:
        print(f"❌ Requests: {e}")

if __name__ == "__main__":
    diagnose_environment()
