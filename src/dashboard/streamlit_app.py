import streamlit as st
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Configuration de la page
st.set_page_config(
    page_title="🏃‍♂️ Strava Analytics",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4b4b;
    }
    .stMetric > label {
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

def format_pace_display(pace_value):
    """
    Convertit la valeur pace_min_per_km (format 4.30) en affichage MM:SS
    Exemple: 4.30 -> "4:30", 5.05 -> "5:05"
    """
    if pd.isna(pace_value) or pace_value <= 0:
        return "N/A"
    
    # Extraire les minutes (partie entière)
    minutes = int(pace_value)
    
    # Extraire les secondes (partie décimale * 100)
    seconds = int(round((pace_value - minutes) * 100))
    
    # S'assurer que les secondes ne dépassent pas 59
    if seconds >= 60:
        minutes += seconds // 60
        seconds = seconds % 60
    
    return f"{minutes}:{seconds:02d}"

def format_duration_display(minutes):
    """
    Convertit les minutes en format HH:MM
    Exemple: 65 -> "1:05", 120 -> "2:00"
    """
    if pd.isna(minutes) or minutes <= 0:
        return "N/A"
    
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    return f"{hours}:{mins:02d}"

def run_data_extraction():
    """Lance l'extraction des données Strava"""
    try:
        # Ajouter le chemin vers l'extracteur
        current_dir = os.path.dirname(os.path.abspath(__file__))
        extract_dir = os.path.join(current_dir, '..', 'extract')
        sys.path.insert(0, extract_dir)
        
        # Importer et exécuter l'extracteur
        from strava_extractor import main as extract_main
        extract_main()
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de l'extraction: {e}")
        return False

def ensure_data_exists():
    """S'assure que les données existent"""
    # Chercher la base de données dans différents emplacements
    possible_paths = [
        'data/strava.duckdb',
        '../../data/strava.duckdb',
        '../data/strava.duckdb'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return True, path
    
    # Si aucune base trouvée, proposer l'extraction
    st.warning("⚠️ Aucune donnée trouvée")
    
    if st.button("🔄 Extraire les données Strava"):
        with st.spinner("Extraction en cours..."):
            if run_data_extraction():
                st.success("✅ Extraction terminée!")
                st.rerun()
            else:
                st.error("❌ Échec de l'extraction")
    
    return False, None

@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_data():
    """Charge les données depuis DuckDB"""
    try:
        # Vérifier que les données existent
        data_exists, db_path = ensure_data_exists()
        if not data_exists:
            return None, None, None, None
        
        st.sidebar.success(f"✅ Base de données connectée")

        conn = duckdb.connect(db_path)
        
        # Charger les différentes tables
        activities = conn.execute("SELECT * FROM activities_summary ORDER BY start_date DESC").df()
        monthly_stats = conn.execute("SELECT * FROM monthly_stats ORDER BY activity_month DESC").df()
        performance_trends = conn.execute("SELECT * FROM performance_trends ORDER BY activity_month DESC, sport_type").df()
        
        # Données brutes pour analyses spécifiques
        raw_activities = conn.execute("""
            SELECT 
                activity_id, activity_name, sport_type, start_date, distance_km,
                moving_time_minutes, average_speed_kmh, pace_min_per_km,
                total_elevation_gain_m, average_heartrate, activity_date
            FROM activities_summary 
            ORDER BY start_date DESC
        """).df()
        
        conn.close()
        
        return activities, monthly_stats, performance_trends, raw_activities
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {e}")
        return None, None, None, None


def display_kpis(activities_df):
    """Affiche les KPIs principaux"""
    if activities_df is None or activities_df.empty:
        st.warning("Aucune donnée disponible")
        return
    
    # Calculs des KPIs
    total_activities = len(activities_df)
    total_distance = activities_df['distance_km'].sum()
    total_time_hours = activities_df['moving_time_minutes'].sum()
    avg_pace = activities_df['pace_min_per_km'].mean()
    total_elevation = activities_df['total_elevation_gain_m'].sum()
    
    # Affichage en colonnes
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🏃‍♂️ Total Activités",
            value=f"{total_activities}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📏 Distance Totale",
            value=f"{total_distance:.0f} km",
            delta=None
        )
    
    with col3:
        # Formatage du temps total en HH:MM
        total_time_formatted = format_duration_display(total_time_hours)
        st.metric(
            label="⏱️ Temps Total",
            value=total_time_formatted,
            delta=None
        )
    
    with col4:
        # Formatage de l'allure en MM:SS
        avg_pace_formatted = format_pace_display(avg_pace)
        st.metric(
            label="⚡ Allure Moyenne",
            value=avg_pace_formatted,
            delta=None
        )
    
    with col5:
        st.metric(
            label="⛰️ Dénivelé Total",
            value=f"{total_elevation:.0f} m",
            delta=None
        )

def plot_monthly_evolution(monthly_stats_df):
    """Graphique d'évolution mensuelle"""
    if monthly_stats_df is None or monthly_stats_df.empty:
        st.warning("Aucune donnée mensuelle disponible")
        return
    
    # Préparer les données
    df = monthly_stats_df.copy()
    df['month_str'] = df['activity_month'].dt.strftime('%Y-%m')
    
    # Graphique avec deux axes Y
    fig = go.Figure()
    
    # Distance (axe principal)
    fig.add_trace(go.Scatter(
        x=df['month_str'],
        y=df['total_distance_km'],
        mode='lines+markers',
        name='Distance (km)',
        line=dict(color='#ff4b4b', width=3),
        marker=dict(size=8)
    ))
    
    # Nombre d'activités (axe secondaire)
    fig.add_trace(go.Scatter(
        x=df['month_str'],
        y=df['total_activities'],
        mode='lines+markers',
        name='Nb Activités',
        yaxis='y2',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    # Configuration des axes
    fig.update_layout(
        title="📈 Évolution Mensuelle",
        xaxis_title="Mois",
        yaxis=dict(
            title="Distance (km)",
            side="left",
            color='#ff4b4b',
            range=[0, None] # Commence à 0
        ),
        yaxis2=dict(
            title="Nombre d'activités",
            side="right",
            overlaying="y",
            color='#1f77b4',
            range=[0, None] # Commence à 0
        ),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_recent_activities_trends(activities_df):
    """Line chart des 5 dernières activités avec distance et temps"""
    if activities_df is None or activities_df.empty:
        return
    
    # Prendre les 5 dernières activités
    recent_5 = activities_df.head(5).copy()
    
    if len(recent_5) < 2:
        st.warning("Pas assez d'activités pour afficher les tendances")
        return
    
    # Préparer les données (inverser l'ordre pour avoir chronologique)
    recent_5 = recent_5.iloc[::-1].reset_index(drop=True)
    
    # Formater les dates pour l'axe X
    recent_5['start_date'] = pd.to_datetime(recent_5['start_date'])
    recent_5['date_label'] = recent_5['start_date'].dt.strftime('%d/%m')
    
    # Créer le graphique avec axes multiples
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=["📈 Tendances des 5 Dernières Activités"]
    )
    
    # Distance (axe principal gauche)
    fig.add_trace(
        go.Scatter(
            x=recent_5['date_label'],
            y=recent_5['distance_km'],
            mode='lines+markers',
            name='Distance (km)',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10, symbol='circle'),
            hovertemplate='<b>%{customdata}</b><br>' +
                         'Date: %{x}<br>' +
                         'Distance: %{y:.2f} km<extra></extra>',
            customdata=recent_5['activity_name']
        ),
        secondary_y=False
    )
    
    # Temps en minutes (axe secondaire droit)
    fig.add_trace(
        go.Scatter(
            x=recent_5['date_label'],
            y=recent_5['moving_time_minutes'],
            mode='lines+markers',
            name='Temps (min)',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=10, symbol='square'),
            hovertemplate='<b>%{customdata}</b><br>' +
                         'Date: %{x}<br>' +
                         'Temps: %{y:.0f} min<extra></extra>',
            customdata=recent_5['activity_name'],
            yaxis='y2'
        ),
        secondary_y=True
    )
    
    # Configuration des axes
    fig.update_xaxes(
        title_text="Date",
        tickangle=0
    )

    fig.update_layout(
        yaxis=dict(
            title="Distance (km)",
            side="left",
            color='#1f77b4',
            range=[0, None],  # Explicitement de 0 au maximum
            showgrid=True
        ),
        yaxis2=dict(
            title="Temps (minutes)",
            side="right",
            overlaying="y",
            color='#ff7f0e',
            range=[0, None],  # Explicitement de 0 au maximum
            showgrid=False
        )
    )
    
    # Mise en page
    fig.update_layout(
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(b=60)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    



def plot_distance_categories(activities_df):
    """Répartition par catégories de distance"""
    if activities_df is None or activities_df.empty:
        return
    
    # Compter par catégorie
    category_counts = activities_df['distance_category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="🎯 Répartition par Distance",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def plot_weekly_heatmap(activities_df):
    """Heatmap des activités par jour de la semaine et heure"""
    if activities_df is None or activities_df.empty:
        return
    
    # Préparer les données
    df = activities_df.copy()
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['day_of_week'] = df['start_date'].dt.day_name()
    df['hour'] = df['start_date'].dt.hour
    
    # Créer une matrice pour la heatmap
    heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    
    # Pivot pour la heatmap
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
    
    # Réorganiser les jours de la semaine
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    
    fig = px.imshow(
        heatmap_pivot,
        title="🗓️ Activités par Jour et Heure",
        labels=dict(x="Heure", y="Jour", color="Nb Activités"),
        color_continuous_scale="Reds"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def display_recent_activities(activities_df):
    """Tableau des activités récentes"""
    if activities_df is None or activities_df.empty:
        return
    
    st.subheader("🕐 Activités Récentes")
    
    # Sélectionner les colonnes importantes
    recent_activities = activities_df.head(15)[[
        'activity_name', 'sport_type', 'start_date', 'distance_km',
        'moving_time_minutes', 'pace_min_per_km', 'total_elevation_gain_m'
    ]].copy()
    
    # Formater les données
    recent_activities['start_date'] = pd.to_datetime(recent_activities['start_date']).dt.strftime('%d/%m/%Y %H:%M')
    recent_activities['distance_km'] = recent_activities['distance_km'].round(2)
    
    # Formatage du temps en HH:MM
    recent_activities['moving_time_formatted'] = recent_activities['moving_time_minutes'].apply(format_duration_display)
    
    # Formatage de l'allure en MM:SS
    recent_activities['pace_formatted'] = recent_activities['pace_min_per_km'].apply(format_pace_display)
    
    recent_activities['total_elevation_gain_m'] = recent_activities['total_elevation_gain_m'].round(0).astype(int)
    
    # Sélectionner les colonnes finales avec formatage
    display_df = recent_activities[[
        'activity_name', 'sport_type', 'start_date', 'distance_km',
        'moving_time_formatted', 'pace_formatted', 'total_elevation_gain_m'
    ]].copy()
    
    # Renommer les colonnes
    display_df.columns = [
        'Activité', 'Sport', 'Date', 'Distance (km)',
        'Temps', 'Allure', 'Dénivelé (m)'
    ]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def main():
    """Fonction principale du dashboard"""
    
    # Titre principal
    st.title("🏃‍♂️ Mon Dashboard Strava")
    st.markdown("---")
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        activities, monthly_stats, performance_trends, raw_activities = load_data()
    
    if activities is None:
        st.error("Impossible de charger les données. Vérifiez que l'extraction Strava a été effectuée.")
        st.stop()
    
    # Sidebar pour les filtres
    st.sidebar.header("🔧 Filtres")
    
    # Filtre par sport
    sports = ['Tous'] + list(activities['sport_type'].unique())
    selected_sport = st.sidebar.selectbox("Sport", sports)
    
    # Filtre par période
    date_range = st.sidebar.date_input(
        "Période",
        value=(activities['activity_date'].min(), activities['activity_date'].max()),
        min_value=activities['activity_date'].min(),
        max_value=activities['activity_date'].max()
    )
    
    # Appliquer les filtres
    filtered_activities = activities.copy()
    
    if selected_sport != 'Tous':
        filtered_activities = filtered_activities[filtered_activities['sport_type'] == selected_sport]
    
    if len(date_range) == 2:
        filtered_activities = filtered_activities[
            (filtered_activities['activity_date'] >= pd.to_datetime(date_range[0])) &
            (filtered_activities['activity_date'] <= pd.to_datetime(date_range[1]))
        ]
    
    # Affichage des KPIs
    st.subheader("📊 Indicateurs Clés")
    display_kpis(filtered_activities)
    
    st.markdown("---")
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        plot_monthly_evolution(monthly_stats)
        plot_distance_categories(filtered_activities)
    
    with col2:
        plot_recent_activities_trends(filtered_activities)
        plot_weekly_heatmap(filtered_activities)
    
    st.markdown("---")
    
    # Tableau des activités récentes
    display_recent_activities(filtered_activities)
    
    # Informations de mise à jour
    st.sidebar.markdown("---")
    st.sidebar.info(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.sidebar.info(f"📈 {len(activities)} activités au total")

if __name__ == "__main__":
    main()
