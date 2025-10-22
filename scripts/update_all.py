#!/usr/bin/env python3
"""
Script d'automatisation locale complète
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_command(command, description, cwd=None):
    """Exécute une commande et gère les erreurs"""
    logging.info(f"🔄 {description}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        logging.info(f"✅ {description} - Succès")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ {description} - Erreur: {e.stderr}")
        return False

def main():
    """Processus complet d'automatisation"""
    start_time = datetime.now()
    logging.info("🚀 Début de l'automatisation Strava Analytics")
    
    # Étape 1: Extraction des données Strava
    if not run_command(
        "python src/extract/strava_extractor.py",
        "Extraction des données Strava"
    ):
        logging.error("❌ Échec de l'extraction")
        return False
    
    # Étape 2: Transformation dbt
    if not run_command(
        "dbt run --profiles-dir .",
        "Transformation des données (dbt)",
        cwd="src/transform/dbt_project"
    ):
        logging.error("❌ Échec de la transformation")
        return False
    
    # Étape 3: Tests dbt
    run_command(
        "dbt test --profiles-dir .",
        "Tests de qualité des données",
        cwd="src/transform/dbt_project"
    )
    
    # Étape 4: Commit et push (si dans un repo git)
    if os.path.exists('.git'):
        run_command(
            'git add data/strava.duckdb* && git commit -m "🤖 Auto-update data" && git push',
            "Commit et push des données"
        )
    
    # Résumé
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"🎉 Automatisation terminée en {duration.total_seconds():.1f} secondes")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
