"""
Point d'entrée pour Streamlit Cloud
"""
import sys
import os

# Ajouter le chemin vers le dashboard
current_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_path = os.path.join(current_dir, 'src', 'dashboard')
sys.path.insert(0, dashboard_path)

# Importer le dashboard
try:
    from streamlit_app import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    import streamlit as st
    st.error(f"❌ Erreur d'import du dashboard: {e}")
    st.info("🔧 Vérifiez la structure du projet")
