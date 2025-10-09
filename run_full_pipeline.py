import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description, cwd=None):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    print(f"💻 Commande : {' '.join(command)}")
    
    try:
        # Configuration spéciale pour Windows et l'encodage
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Utiliser shell=True sur Windows pour éviter les problèmes d'encodage
        if sys.platform == "win32":
            # Joindre la commande en string pour Windows
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in command)
            result = subprocess.run(
                cmd_str,
                cwd=cwd,
                shell=True,
                env=env,
                text=True,
                capture_output=True,
                encoding='utf-8',
                errors='replace'
            )
        else:
            # Unix/Linux - utiliser la méthode normale
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                text=True,
                capture_output=True,
                encoding='utf-8',
                errors='replace'
            )
        
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            # Afficher la sortie si elle existe et n'est pas vide
            if result.stdout and result.stdout.strip():
                print("📄 Sortie :")
                print(result.stdout.strip())
            return True
        else:
            print(f"❌ {description} - Échec (code {result.returncode})")
            if result.stderr and result.stderr.strip():
                print("📄 Erreur :")
                print(result.stderr.strip())
            return False
            
    except Exception as e:
        print(f"❌ {description} - Erreur inattendue : {e}")
        return False

def main():
    """Pipeline complet d'extraction, transformation et visualisation"""
    
    print("🏃‍♂️ PIPELINE STRAVA ANALYTICS COMPLET")
    print("=" * 50)
    print(f"🕐 Début : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifications préliminaires
    print("\n🔍 Vérifications préliminaires...")
    
    # Vérifier que les fichiers existent
    required_files = [
        "src/extract/strava_extractor.py",
        ".env"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Fichier manquant : {file_path}")
            return
        else:
            print(f"✅ {file_path}")
    
    # Vérifier que dbt est installé
    try:
        result = subprocess.run(["dbt", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ dbt installé")
        else:
            print("❌ dbt non trouvé")
            return
    except:
        print("❌ dbt non trouvé")
        return
    
    print("\n" + "="*50)
    
    # Étape 1 : Extraction des données
    if not run_command(
        [sys.executable, "src/extract/strava_extractor.py"],
        "Extraction des données Strava"
    ):
        print("❌ Arrêt du pipeline - Échec de l'extraction")
        return
    
    # Étape 2 : Transformations dbt
    dbt_path = "src/transform/dbt_project"
    if not os.path.exists(dbt_path):
        print(f"❌ Dossier dbt non trouvé : {dbt_path}")
        return
        
    if not run_command(
        ["dbt", "run"],
        "Transformations dbt",
        cwd=dbt_path
    ):
        print("❌ Arrêt du pipeline - Échec des transformations")
        return
    
    # Étape 3 : Tests dbt (optionnel)
    print("\n🧪 Tests de qualité (optionnel)...")
    if not run_command(
        ["dbt", "test"],
        "Tests de qualité dbt",
        cwd=dbt_path
    ):
        print("⚠️ Attention - Certains tests ont échoué, mais on continue")
    
    # Étape 4 : Vérification des données (optionnel)
    if os.path.exists("check_transformed_data.py"):
        print("\n🔍 Vérification des données...")
        if not run_command(
            [sys.executable, "check_transformed_data.py"],
            "Vérification des données transformées"
        ):
            print("⚠️ Attention - Problème de vérification, mais on continue")
    
    print("\n" + "=" * 50)
    print("🎉 PIPELINE TERMINÉ AVEC SUCCÈS !")
    print(f"🕐 Fin : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 Pour lancer le dashboard :")
    print("   python run_dashboard.py")
    print("   ou")
    print("   streamlit run src/dashboard/streamlit_app.py")

if __name__ == "__main__":
    main()
