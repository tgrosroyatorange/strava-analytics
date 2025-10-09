# 🏃‍♂️ Strava Analytics Dashboard

Un pipeline complet d'analyse des données Strava avec extraction automatique, transformations dbt et dashboard interactif Streamlit.

## 🎯 Fonctionnalités

- **📥 Extraction automatique** des données depuis l'API Strava
- **🔄 Transformations** avec dbt (nettoyage, agrégations, métriques)
- **📊 Dashboard interactif** avec Streamlit et Plotly
- **🧪 Tests de qualité** des données
- **🚀 Pipeline automatisé** complet

## 📊 Métriques disponibles

### KPIs principaux
- Total des activités et distance parcourue
- Temps total d'entraînement
- Allure moyenne et dénivelé cumulé

### Analyses avancées
- Évolution mensuelle des performances
- Distribution des allures
- Répartition par catégories de distance
- Heatmap des activités par jour/heure
- Tendances de performance

## 🚀 Installation et Configuration

### 1. Prérequis

Assurez-vous d'avoir installé :
- **Python 3.11+**
- **Git**

### 2. Cloner le repository
```bash
git clone https://github.com/votre-username/strava-analytics.git
cd strava-analytics
```
### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```
### 4. Configuration Strava API
    
#### A. Créer une application Strava

1. Allez sur https://developers.strava.com/
2. Cliquez sur "Create & Manage Your App"
3. Remplissez le formulaire :
    - Application Name : Mon Analytics Strava
    - Category : Data Importer
    - Club : Laissez vide
    - Website : http://localhost
    - Authorization Callback Domain : localhost
4. Cliquez sur "Create"
5. Notez votre Client ID et Client Secret

#### B. Configurer les variables d'environnement

##### 1. Copiez le fichier d'exemple

```bash
cp .env.example .env
```

##### 2. Éditez le fichier .env avec vos credentials :

```bash
# Configuration Strava API
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
STRAVA_REFRESH_TOKEN=your_refresh_token_here
```

#### C. Obtenir le refresh token **(non testé)**

##### 1. Exécutez le script d'autorisation :
```bash
python get_token.py
```

##### 2. Suivez les instructions ;
- Une URL s'affichera dans votre terminal
- Copiez-collez cette URL dans votre navigateur
- Autorisez l'application Strava
- Copiez le code d'autorisation depuis l'URL de redirection
- Collez-le dans le terminal

##### 3. Le refresh token sera automatiquement ajouté à votre fichier .env

#### 4. Test de la configuration 
```bash
# Tester la connexion Strava
python src/extract/strava_extractor.py

# Vérifier la configuration complète
python debug_dashboard.py
```

## 🔄 Utilisation

### Pipeline complet (première fois)
```bash

# Extraction + Transformations + Tests
python run_full_pipeline.py
```

### Mise à jour quotidienne (recommandé)
```bash

# Mise à jour (seulement les nouvelles activités)
python update_data.py
```

### Lancer le dashboard
```bash

python run_dashboard.py
```
Le dashboard sera accessible sur http://localhost:8501

### Commandes individuelles
#### Extraction des données

```bash
# Extraction complète
python src/extract/strava_extractor.py

# Vérifier les données extraites
python check_raw_data.py
```

#### Transformations dbt

```bash
cd src/transform/dbt_project

# Exécuter les transformations
dbt run

# Lancer les tests de qualité
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve

# Retourner à la racine
cd ../../..
```


#### Vérufucation des données

```bash
# Vérifier les données transformées
python check_transformed_data.py

# Diagnostic complet du dashboard
python debug_dashboard.py
```

## 📁 Structure du projet
    strava-analytics/
    ├── 📄 README.md
    ├── 📄 requirements.txt
    ├── 📄 .env.example
    ├── 📄 .env
    ├── 📄 .gitignore
    ├── 🚀 run_full_pipeline.py          # Pipeline complet
    ├── 🚀 run_dashboard.py              # Lancement du dashboard
    ├── 🔄 update_data.py                # Mise à jour incrémentale
    ├── 🔍 check_transformed_data.py     # Vérification des données
    ├── 🔍 check_raw_data.py             # Vérification extraction
    ├── 🔍 debug_dashboard.py            # Diagnostic dashboard
    ├── 🔑 get_token.py                  # Obtention du token Strava
    ├── 📂 src/
    │   ├── 📂 extract/
    │   │   └── 📄 strava_extractor.py   # Extraction API Strava
    │   ├── 📂 transform/
    │   │   └── 📂 dbt_project/
    │   │       ├── 📄 dbt_project.yml
    │   │       ├── 📄 profiles.yml
    │   │       ├── 📂 models/
    │   │       │   ├── 📂 staging/
    │   │       │   │   └── 📄 stg_strava_activities.sql
    │   │       │   └── 📂 marts/
    │   │       │       ├── 📄 activities_summary.sql
    │   │       │       ├── 📄 monthly_stats.sql
    │   │       │       └── 📄 performance_trends.sql
    │   │       ├── 📂 tests/
    │   │       └── 📂 macros/
    │   └── 📂 dashboard/
    │       ├── 📄 streamlit_app.py      # Interface Streamlit
    │       └── 📄 config.py             # Configuration dashboard
    ├── 📂 data/
    │   └── 💾 strava.duckdb             # Base de données
    └── 📂 .github/
        └── 📂 workflows/
            └── 📄 update_data.yml       # CI/CD (optionnel)


## 🛠️ Technologies utilisées
* Python 3.11+ - Langage principal
* DuckDB - Base de données analytique
* dbt - Transformations de données
* Streamlit - Interface web interactive
* Plotly - Visualisations interactives
* Strava API - Source des données
* Pandas - Manipulation de données
* Requests - Appels API

## 📈 Modèles de données

### Staging 
**stg_strava_activities** - Données nettoyées et standardisées

### Marts 
**activities_summary** - Vue consolidée des activités

**monthly_stats** - Statistiques mensuelles aggrégées

**performance_trends** - Evolution des performances

## 🔄 Workflows recommandés

### Usage quotidien
```bash
# Après vos courses
python update_data.py      # ~5-10 secondes
python run_dashboard.py    # Analyser vos performances
```

### Maintenance hebdomadaire
 ```bash
# Vérification complète
python run_full_pipeline.py
python debug_dashboard.py
```

### Développement
 ```bash
# Modifier les modèles dbt
cd src/transform/dbt_project
dbt run --select model_name
dbt test --select model_name

# Tester le dashboard
streamlit run src/dashboard/streamlit_app.py
```

## 🚨 Résolution de problèmes

### Problème d'extraction
 ```bash
# Vérifier les credentials
python get_token.py

# Test manuel
python src/extract/strava_extractor.py
```

### Problème de transformations 
 ```bash
cd src/transform/dbt_project

# Debug dbt
dbt debug
dbt run --full-refresh
```

### Problème de dashboard
```bash
# Diagnostic complet
python debug_dashboard.py

# Vérifier les données
python check_transformed_data.py
```

### Erreurs d'encodage (Windows)
```bash
Si vous rencontrez des erreurs Unicode :

# Définir l'encodage
set PYTHONIOENCODING=utf-8
python update_data.py
```

# **🏃‍♂️ Happy running and analyzing! 🏃‍♀️**