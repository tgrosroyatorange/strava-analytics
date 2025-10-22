"""
Point d'entrée pour Streamlit Cloud avec extraction automatique
"""
import sys
import os
import streamlit as st

# Ajouter le chemin vers le dashboard
current_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_path = os.path.join(current_dir, 'src', 'dashboard')
sys.path.insert(0, dashboard_path)

def main():
    """Point d'entrée principal"""
    
    # Vérifier si les données existent
    data_exists = os.path.exists('data/strava.duckdb')
    
    if not data_exists:
        st.warning("⚠️ Première visite - Extraction des données en cours...")
        
        # Bouton pour lancer l'extraction
        if st.button("🔄 Extraire les données Strava"):
            with st.spinner("Extraction en cours..."):
                try:
                    # Lancer l'extraction
                    extract_path = os.path.join(current_dir, 'src', 'extract')
                    sys.path.insert(0, extract_path)
                    
                    from strava_extractor import main as extract_main
                    extract_main()
                    
                    # Lancer la transformation
                    import subprocess
                    dbt_path = os.path.join(current_dir, 'src', 'transform', 'dbt_project')
                    subprocess.run(['dbt', 'run', '--profiles-dir', '.'], cwd=dbt_path, check=True)
                    
                    st.success("✅ Données extraites et transformées !")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'extraction: {e}")
                    st.info("🔄 Les données seront mises à jour automatiquement par GitHub Actions")
        
        st.info("💡 Les données sont mises à jour automatiquement 2 fois par jour")
        st.stop()
    
    # Charger le dashboard principal
    try:
        from streamlit_app import main as dashboard_main
        dashboard_main()
    except ImportError as e:
        st.error(f"❌ Erreur d'import du dashboard: {e}")

if __name__ == "__main__":
    main()
