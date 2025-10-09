import subprocess
import sys
import os

def run_dashboard():
    """Lance le dashboard Streamlit"""
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('src/dashboard/streamlit_app.py'):
        print("❌ Fichier streamlit_app.py non trouvé")
        print("Assurez-vous d'être dans le répertoire racine du projet")
        return
    
    # Vérifier que la base de données existe
    if not os.path.exists('data/strava.duckdb'):
        print("❌ Base de données non trouvée")
        print("Exécutez d'abord : python src/extract/strava_extractor.py")
        return
    
    # Vérifier que les transformations dbt ont été exécutées
    try:
        import duckdb
        conn = duckdb.connect('data/strava.duckdb')
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        
        required_tables = ['activities_summary', 'monthly_stats']
        missing_tables = [table for table in required_tables if table not in table_names]
        
        if missing_tables:
            print(f"❌ Tables manquantes : {', '.join(missing_tables)}")
            print("Exécutez d'abord les transformations dbt :")
            print("  cd src/transform/dbt_project")
            print("  dbt run")
            conn.close()
            return
        
        conn.close()
        print("✅ Toutes les données sont prêtes")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return
    
    print("🚀 Lancement du dashboard Streamlit...")
    print("📱 Le dashboard s'ouvrira dans votre navigateur")
    print("🌐 URL locale : http://localhost:8501")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    print("-" * 50)
    
    try:
        # Lancer Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/dashboard/streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard arrêté")
    except Exception as e:
        print(f"❌ Erreur lors du lancement : {e}")
        print("\nEssayez manuellement :")
        print("streamlit run src/dashboard/streamlit_app.py")

if __name__ == "__main__":
    run_dashboard()
