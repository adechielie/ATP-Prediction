"""
Application Streamlit pour la prédiction de matchs ATP.
Interface web moderne pour todoba.net

NOUVEAU : Affichage des joueurs les plus actifs de l'année en cours
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime

# 🔵 AJOUT ML
from src.ml.inference import MatchPredictor


# Configuration de la page
st.set_page_config(
    page_title="ATP Match Prediction | todoba.net",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .prediction-box {
        padding: 2rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .active-player-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #10b981;
        color: white;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_active_players(df: pd.DataFrame, years: int = 2):
    """
    Récupère la liste des joueurs ayant joué dans les N dernières années.
    
    Args:
        df: DataFrame avec les matchs
        years: Nombre d'années à considérer comme "actif"
    
    Returns:
        Liste triée des joueurs actifs
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=years * 365)
    
    # Filtrer les matchs récents
    recent_matches = df[df['tourney_date'] >= cutoff_date]
    
    # Obtenir les joueurs uniques (P1 et P2)
    active_players = set(recent_matches['P1'].unique()) | set(recent_matches['P2'].unique())
    
    return sorted(list(active_players))


@st.cache_data
def load_data():
    """Charge les données gold (avec cache)."""
    try:
        gold_path = Path("data/gold/atp_matches_gold.csv")
        if gold_path.exists():
            df = pd.read_csv(gold_path)
            df['tourney_date'] = pd.to_datetime(df['tourney_date'])
            return df
        else:
            st.error("⚠️ Données non trouvées. Exécutez d'abord run_pipeline.py")
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None


@st.cache_data
def get_most_active_players_current_year(df: pd.DataFrame, top_n: int = 20):
    """
    Récupère les joueurs les plus actifs de l'année en cours.
    
    Args:
        df: DataFrame avec les matchs
        top_n: Nombre de joueurs à retourner
    
    Returns:
        DataFrame avec les joueurs les plus actifs
    """
    current_year = datetime.now().year
    
    # Filtrer les matchs de l'année en cours
    df_current_year = df[df['tourney_date'].dt.year == current_year]
    
    if len(df_current_year) == 0:
        # Si pas de données cette année, prendre l'année dernière
        current_year = df['tourney_date'].dt.year.max()
        df_current_year = df[df['tourney_date'].dt.year == current_year]
    
    # Compter les matchs par joueur (P1 et P2)
    p1_counts = df_current_year['P1'].value_counts()
    p2_counts = df_current_year['P2'].value_counts()
    
    # Combiner les compteurs
    total_counts = p1_counts.add(p2_counts, fill_value=0).sort_values(ascending=False)
    
    # Créer un DataFrame avec les stats
    active_players = []
    
    for player, match_count in total_counts.head(top_n).items():
        player_matches = df_current_year[
            (df_current_year['P1'] == player) | (df_current_year['P2'] == player)
        ]
        
        # Calculer le nombre de victoires
        wins = len(player_matches[player_matches['P1'] == player])
        win_rate = (wins / match_count * 100) if match_count > 0 else 0
        
        # Dernier match
        last_match_date = player_matches['tourney_date'].max()
        
        # ELO moyen (si disponible)
        player_p1_matches = df_current_year[df_current_year['P1'] == player]
        avg_elo = player_p1_matches['P1_elo'].mean() if 'P1_elo' in player_p1_matches.columns and len(player_p1_matches) > 0 else None
        
        active_players.append({
            'Joueur': player,
            'Matchs': int(match_count),
            'Victoires': wins,
            'Win Rate (%)': round(win_rate, 1),
            'ELO Moyen': round(avg_elo) if avg_elo is not None else 'N/A',
            'Dernier Match': last_match_date.strftime('%d/%m/%Y') if pd.notna(last_match_date) else 'N/A'
        })
    
    return pd.DataFrame(active_players), current_year


# 🔵 CACHE DU MODÈLE ML
@st.cache_resource
def load_predictor():
    """Charge le modèle de Machine Learning pour l'inférence."""
    return MatchPredictor()


def get_player_stats(df: pd.DataFrame, player_name: str, n_matches: int = 5):
    """
    Récupère les statistiques récentes d'un joueur.
    
    Args:
        df: DataFrame avec les matchs
        player_name: Nom du joueur
        n_matches: Nombre de matchs récents à considérer
    
    Returns:
        Dict avec les statistiques
    """
    player_matches = df[df['P1'] == player_name].sort_values('tourney_date', ascending=False)
    
    if len(player_matches) == 0:
        return None
    
    recent = player_matches.head(n_matches)
    
    stats = {
        'total_matches': len(player_matches),
        'recent_matches': len(recent),
        'win_rate': (recent['result'] == 1).mean(),
        'avg_elo': recent['P1_elo'].mean() if 'P1_elo' in recent.columns else 1500,
        'avg_rank': recent['P1_rank_moy'].mean() if 'P1_rank_moy' in recent.columns else recent['P1_rank'].mean(),
        'avg_aces': recent['P1_ace_moy'].mean() if 'P1_ace_moy' in recent.columns else recent['P1_ace'].mean(),
        'avg_df': recent['P1_df_moy'].mean() if 'P1_df_moy' in recent.columns else recent['P1_df'].mean(),
        'surface_performance': recent.groupby('surface').apply(lambda x: (x['result'] == 1).mean()).to_dict(),
        'last_tournament': recent.iloc[0]['tourney_name'] if len(recent) > 0 else "N/A",
        'last_match_date': recent.iloc[0]['tourney_date'] if len(recent) > 0 else None
    }
    
    return stats


def plot_player_performance(df: pd.DataFrame, player_name: str):
    """Graphique de performance du joueur."""
    player_data = df[df['P1'] == player_name].sort_values('tourney_date')
    
    if len(player_data) == 0:
        return None
    
    # ELO rating over time
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=player_data['tourney_date'],
        y=player_data['P1_elo'] if 'P1_elo' in player_data.columns else [1500] * len(player_data),
        mode='lines+markers',
        name='ELO Rating',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=f"Évolution ELO - {player_name}",
        xaxis_title="Date",
        yaxis_title="ELO Rating",
        template="plotly_white",
        height=400
    )
    
    return fig


def plot_surface_performance(stats: dict):
    """Graphique de performance par surface."""
    surfaces = list(stats['surface_performance'].keys())
    win_rates = [stats['surface_performance'][s] * 100 for s in surfaces]
    
    fig = go.Figure(data=[
        go.Bar(
            x=surfaces,
            y=win_rates,
            marker=dict(
                color=win_rates,
                colorscale='Viridis',
                showscale=False
            ),
            text=[f"{wr:.1f}%" for wr in win_rates],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Taux de victoire par surface",
        xaxis_title="Surface",
        yaxis_title="Win Rate (%)",
        template="plotly_white",
        height=350
    )
    
    return fig


def plot_active_players_chart(df_active: pd.DataFrame):
    """Graphique des joueurs les plus actifs."""
    fig = go.Figure()
    
    # Barres pour les matchs
    fig.add_trace(go.Bar(
        name='Matchs joués',
        x=df_active['Joueur'].head(10),
        y=df_active['Matchs'].head(10),
        marker=dict(color='#667eea'),
        text=df_active['Matchs'].head(10),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Top 10 des joueurs les plus actifs (année en cours)",
        xaxis_title="Joueur",
        yaxis_title="Nombre de matchs",
        template="plotly_white",
        height=400,
        showlegend=False
    )
    
    return fig


def calculate_match_odds(df: pd.DataFrame, player1: str, player2: str):
    """
    Calcule les cotes d'un match (version simplifiée).
    
    Args:
        df: DataFrame avec les matchs
        player1: Nom joueur 1
        player2: Nom joueur 2
    
    Returns:
        Dict avec les probabilités
    """
    # Récupérer les stats récentes
    p1_data = df[df['P1'] == player1].sort_values('tourney_date', ascending=False).head(1)
    p2_data = df[df['P1'] == player2].sort_values('tourney_date', ascending=False).head(1)
    
    if p1_data.empty or p2_data.empty:
        return {
            'player1': 0.5,
            'player2': 0.5,
            'confidence': 'low'
        }
    
    # Calculer probabilité basée sur ELO (formule ELO standard)
    p1_elo = p1_data['P1_elo'].iloc[0] if 'P1_elo' in p1_data.columns else 1500
    p2_elo = p2_data['P1_elo'].iloc[0] if 'P1_elo' in p2_data.columns else 1500
    
    prob_p1 = 1 / (1 + 10 ** ((p2_elo - p1_elo) / 400))
    prob_p2 = 1 - prob_p1
    
    # Niveau de confiance basé sur la différence ELO
    elo_diff = abs(p1_elo - p2_elo)
    if elo_diff > 200:
        confidence = 'high'
    elif elo_diff > 100:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    return {
        'player1': prob_p1,
        'player2': prob_p2,
        'confidence': confidence,
        'elo_diff': elo_diff
    }


def main():
    """Application principale."""
    
    # Header
    st.markdown('<h1 class="main-header">🎾 ATP Match Prediction</h1>', unsafe_allow_html=True)
    st.markdown("### Prédisez les résultats de matchs ATP avec le Machine Learning")
    st.markdown("---")
    
    # Charger les données
    df = load_data()
    
    if df is None:
        st.stop()
    
    # Charger le modèle ML
    predictor = load_predictor()
    
    # 🆕 Obtenir uniquement les joueurs ACTIFS (2 dernières années) pour la liste déroulante
    active_players = get_active_players(df, years=2)
    all_players = sorted(df['P1'].unique())  # Gardé pour les stats
    
    # 🆕 SECTION : Joueurs les plus actifs de l'année
    st.markdown("## 🔥 Joueurs les plus actifs")
    
    df_active, current_year = get_most_active_players_current_year(df, top_n=20)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### Classement {current_year}")
        
        # Graphique
        fig_active = plot_active_players_chart(df_active)
        st.plotly_chart(fig_active, use_container_width=True)
    
    with col2:
        st.markdown(f"### Top 5 - {current_year}")
        
        # Afficher le top 5 avec badges
        for idx, row in df_active.head(5).iterrows():
            st.markdown(
                f"""
                <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #667eea;">
                    <strong>#{idx+1} {row['Joueur']}</strong>
                    <span class="active-player-badge">ACTIF</span>
                    <br>
                    <small>
                        {row['Matchs']} matchs • {row['Win Rate (%)']}% WR
                        {f" • ELO {row['ELO Moyen']}" if row['ELO Moyen'] != 'N/A' else ""}
                    </small>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Bouton pour afficher le tableau complet
        with st.expander("📋 Voir le classement complet"):
            st.dataframe(
                df_active,
                use_container_width=True,
                hide_index=True
            )
    
    st.markdown("---")
    
    # Obtenir la liste des joueurs
    players = sorted(df['P1'].unique())
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.atptour.com/-/media/images/atp/atp-tour-logo.jpg", width=200)
        st.markdown("## ⚙️ Configuration")
        
        n_recent_matches = st.slider(
            "Nombre de matchs récents",
            min_value=3,
            max_value=20,
            value=5
        )
        
        st.markdown("---")
        st.markdown("### 📊 Statistiques du dataset")
        st.metric("Joueurs (total)", len(all_players))
        st.metric("Joueurs actifs", len(active_players))
        st.metric("Matchs", f"{len(df):,}")
        st.metric("Joueurs actifs (année)", len(df_active))
        st.metric("Dernière màj", datetime.now().strftime("%d/%m/%Y"))
    
    # Interface principale - Prédiction
    st.markdown("## 🎯 Prédiction de match")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 🆕 Utiliser active_players au lieu de players
        default_p1 = "Rafael Nadal" if "Rafael Nadal" in active_players else active_players[0] if active_players else ""
        player1 = st.selectbox(
            "🎾 Joueur 1 (actifs uniquement)",
            options=active_players,
            index=active_players.index(default_p1) if default_p1 in active_players else 0,
            key="player1",
            help="Liste des joueurs ayant joué dans les 2 dernières années"
        )
    
    with col2:
        # 🆕 Utiliser active_players au lieu de players
        default_p2 = "Novak Djokovic" if "Novak Djokovic" in active_players else active_players[1] if len(active_players) > 1 else ""
        player2 = st.selectbox(
            "🎾 Joueur 2 (actifs uniquement)",
            options=active_players,
            index=active_players.index(default_p2) if default_p2 in active_players else (1 if len(active_players) > 1 else 0),
            key="player2",
            help="Liste des joueurs ayant joué dans les 2 dernières années"
        )
    
    if player1 == player2:
        st.warning("⚠️ Veuillez sélectionner deux joueurs différents")
        st.stop()
    
    # Bouton de prédiction
    if st.button("🔮 PRÉDIRE LE MATCH", use_container_width=True):
        
        # Calcul des probabilités
        with st.spinner("Calcul des probabilités..."):
            try:
                # Prédiction ML
                prob_p1 = predictor.predict_proba(player1, player2)
                prob_p2 = 1 - prob_p1
                odds = {
                    'player1': prob_p1,
                    'player2': prob_p2,
                    'confidence': 'ml',
                    'elo_diff': None
                }
            except ValueError:
                # Fallback ELO (inchangé)
                odds = calculate_match_odds(df, player1, player2)
        
        # Affichage des résultats
        st.markdown("### 📊 Résultat de la prédiction")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="prediction-box">
                <h3>{player1}</h3>
                <div class="metric-value">{odds['player1']*100:.1f}%</div>
                <div class="metric-label">Probabilité de victoire</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding-top: 3rem;">
                <h2 style="color: #667eea;">VS</h2>
                <p style="color: #666;">Confiance: <strong>{odds['confidence'].upper()}</strong></p>
                {"<p style='color: #999; font-size: 0.8rem;'>Δ ELO: " + f"{odds['elo_diff']:.0f}" + "</p>" if odds['elo_diff'] is not None else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="prediction-box">
                <h3>{player2}</h3>
                <div class="metric-value">{odds['player2']*100:.1f}%</div>
                <div class="metric-label">Probabilité de victoire</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Graphique de comparaison
        st.markdown("---")
        
        fig = go.Figure(data=[
            go.Bar(
                name='Probabilité',
                x=[player1, player2],
                y=[odds['player1'] * 100, odds['player2'] * 100],
                marker=dict(
                    color=['#667eea', '#764ba2'],
                ),
                text=[f"{odds['player1']*100:.1f}%", f"{odds['player2']*100:.1f}%"],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Comparaison des probabilités",
            yaxis_title="Probabilité de victoire (%)",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques détaillées
    st.markdown("---")
    st.markdown("## 📊 Statistiques des joueurs")
    
    tab1, tab2 = st.tabs([f"📈 {player1}", f"📈 {player2}"])
    
    with tab1:
        stats1 = get_player_stats(df, player1, n_recent_matches)
        
        if stats1:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("ELO Rating", f"{stats1['avg_elo']:.0f}")
            with col2:
                st.metric("Classement ATP", f"#{stats1['avg_rank']:.0f}")
            with col3:
                st.metric("Win Rate (récent)", f"{stats1['win_rate']*100:.1f}%")
            with col4:
                st.metric("Aces moyens", f"{stats1['avg_aces']:.1f}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = plot_player_performance(df, player1)
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = plot_surface_performance(stats1)
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning(f"Aucune donnée disponible pour {player1}")
    
    with tab2:
        stats2 = get_player_stats(df, player2, n_recent_matches)
        
        if stats2:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("ELO Rating", f"{stats2['avg_elo']:.0f}")
            with col2:
                st.metric("Classement ATP", f"#{stats2['avg_rank']:.0f}")
            with col3:
                st.metric("Win Rate (récent)", f"{stats2['win_rate']*100:.1f}%")
            with col4:
                st.metric("Aces moyens", f"{stats2['avg_aces']:.1f}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = plot_player_performance(df, player2)
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = plot_surface_performance(stats2)
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning(f"Aucune donnée disponible pour {player2}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🎾 ATP Match Prediction | Powered by Machine Learning</p>
        <p>© 2025 <a href="https://todoba.net" target="_blank" style="color: #667eea; text-decoration: none;">todoba.net</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()