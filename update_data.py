import subprocess
import sys
import os
from datetime import datetime

def run_command_safe(command, description, cwd=None):
    """Exécute une commande de manière sécurisée pour l'encodage"""
    print(f"\n📥 {description}...")
    
    try:
        # Configuration spéciale pour Windows et l'encodage
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Utiliser shell=True sur Windows pour éviter les problèmes d'encodage
        if sys.platform == "win32":
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
            if result.stdout and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    clean_line = line.encode('ascii', 'ignore').decode('ascii')
                    if clean_line.strip():
                        print(f"   {clean_line}")
            return True, result.returncode
        else:
            print(f"❌ {description} - Code de retour: {result.returncode}")
            if result.stderr and result.stderr.strip():
                print(f"Erreur : {result.stderr.strip()}")
            return False, result.returncode
            
    except Exception as e:
        print(f"❌ {description} - Erreur inattendue : {e}")
        return False, -1

def update_strava_data():
    """Met à jour les données Strava et les transformations"""
    
    print("🔄 MISE À JOUR DES DONNÉES STRAVA")
    print("=" * 40)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifications préliminaires
    if not os.path.exists('src/extract/strava_extractor.py'):
        print("❌ Script d'extraction non trouvé")
        return False
    
    if not os.path.exists('.env'):
        print("❌ Fichier .env non trouvé")
        return False
    
    try:
        # 1. Extraction (vérifier s'il y a de nouvelles données)
        success, return_code = run_command_safe(
            [sys.executable, "src/extract/strava_extractor.py"],
            "Vérification de nouvelles données Strava"
        )
        
        if not success:
            print("❌ Échec de l'extraction")
            return False
        
        # Si le code de retour est 0 mais qu'il n'y a pas de nouvelles données
        # (le script modifié retourne 0 même sans nouvelles données)
        # On peut détecter cela dans les logs
        
        # 2. Transformations (seulement si il y avait des données à traiter)
        dbt_path = "src/transform/dbt_project"
        if not os.path.exists(dbt_path):
            print(f"❌ Dossier dbt non trouvé : {dbt_path}")
            return False
        
        print("\n🔄 Mise à jour des transformations...")
        success_dbt, _ = run_command_safe(
            ["dbt", "run"],
            "Transformations dbt",
            cwd=dbt_path
        )
        
        if not success_dbt:
            print("❌ Échec des transformations")
            return False
        
        # 3. Vérification rapide (optionnel)
        if os.path.exists("check_transformed_data.py"):
            print("\n🔍 Vérification des données...")
            run_command_safe(
                [sys.executable, "check_transformed_data.py"],
                "Vérification des données"
            )
        
        print("\n" + "=" * 40)
        print("✅ MISE À JOUR TERMINÉE AVEC SUCCÈS !")
        print("🎯 Vos données sont à jour dans le dashboard")
        print("\n🚀 Pour voir vos données :")
        print("   python run_dashboard.py")
        return True
        
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False

def update_strava_data_smart():
    """Version intelligente qui s'arrête s'il n'y a pas de nouvelles données"""
    
    print("🔄 MISE À JOUR INTELLIGENTE DES DONNÉES STRAVA")
    print("=" * 50)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifications préliminaires
    if not os.path.exists('src/extract/strava_extractor.py'):
        print("❌ Script d'extraction non trouvé")
        return False
    
    if not os.path.exists('.env'):
        print("❌ Fichier .env non trouvé")
        return False
    
    try:
        # 1. Extraction avec détection intelligente
        print("\n🔍 Vérification de nouvelles activités...")
        
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        if sys.platform == "win32":
            cmd_str = f'"{sys.executable}" "src/extract/strava_extractor.py"'
            result = subprocess.run(
                cmd_str,
                shell=True,
                env=env,
                text=True,
                capture_output=True,
                encoding='utf-8',
                errors='replace'
            )
        else:
            result = subprocess.run(
                [sys.executable, "src/extract/strava_extractor.py"],
                env=env,
                text=True,
                capture_output=True,
                encoding='utf-8',
                errors='replace'
            )
        
        # Analyser la sortie pour détecter s'il y a de nouvelles données
        output = result.stdout if result.stdout else ""
        
        # Afficher la sortie nettoyée
        if output:
            lines = output.strip().split('\n')
            for line in lines:
                clean_line = line.encode('ascii', 'ignore').decode('ascii')
                if clean_line.strip():
                    print(f"   {clean_line}")
        
        # Vérifier si le processus s'est arrêté car pas de nouvelles données
        if "Aucune nouvelle activite - Processus termine" in output:
            print("\n🎯 AUCUNE NOUVELLE ACTIVITÉ DÉTECTÉE")
            print("✅ Vos données sont déjà à jour !")
            print("📊 Vous pouvez lancer le dashboard : python run_dashboard.py")
            return True  # Succès, mais pas de traitement nécessaire
        
        if result.returncode != 0:
            print("❌ Échec de l'extraction")
            if result.stderr:
                print(f"Erreur : {result.stderr}")
            return False
        
        # Si on arrive ici, il y a de nouvelles données à traiter
        print("✅ Nouvelles données détectées - Poursuite du traitement")
        
        # 2. Transformations dbt
        dbt_path = "src/transform/dbt_project"
        if not os.path.exists(dbt_path):
            print(f"❌ Dossier dbt non trouvé : {dbt_path}")
            return False
        
        success_dbt, _ = run_command_safe(
            ["dbt", "run"],
            "Mise à jour des transformations",
            cwd=dbt_path
        )
        
        if not success_dbt:
            print("❌ Échec des transformations")
            return False
        
        # 3. Vérification rapide (optionnel)
        if os.path.exists("check_transformed_data.py"):
            run_command_safe(
                [sys.executable, "check_transformed_data.py"],
                "Vérification des données"
            )
        
        print("\n" + "=" * 50)
        print("🎉 NOUVELLES DONNÉES TRAITÉES AVEC SUCCÈS !")
        print("🎯 Votre dashboard est maintenant à jour")
        print("\n🚀 Pour voir vos nouvelles données :")
        print("   python run_dashboard.py")
        return True
        
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False

if __name__ == "__main__":
    # Utiliser la version intelligente par défaut
    success = update_strava_data_smart()
    
    if not success:
        print("\n💡 Conseil : Essayez d'exécuter les étapes manuellement :")
        print("   1. python src/extract/strava_extractor.py")
        print("   2. cd src/transform/dbt_project && dbt run")
        sys.exit(1)
