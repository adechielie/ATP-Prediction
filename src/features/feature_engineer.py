"""
Module de feature engineering pour le modèle de prédiction ATP.
Crée des features avancées à partir des données brutes.
"""
from typing import List
import pandas as pd
import numpy as np
from loguru import logger

from ..utils.config import config


class ATPFeatureEngineer:
    """Créateur de features pour le modèle de prédiction."""
    
    def __init__(self):
        self.rolling_window = config.rolling_window
    
    def calculate_rolling_stats(
        self,
        df: pd.DataFrame,
        columns: List[str],
        group_by: str = 'P1'
    ) -> pd.DataFrame:
        """
        Calcule les statistiques moyennes glissantes pour chaque joueur.
        
        Args:
            df: DataFrame avec les matchs
            columns: Colonnes pour lesquelles calculer les moyennes
            group_by: Colonne de groupage (joueur)
        
        Returns:
            DataFrame avec colonnes de moyennes ajoutées
        """
        df = df.copy()
        df = df.sort_values(['P1', 'tourney_date'])
        
        for col in columns:
            if col in df.columns:
                # Moyenne glissante des N derniers matchs
                df[f'{col}_moy'] = (
                    df.groupby(group_by)[col]
                    .rolling(window=self.rolling_window, min_periods=1)
                    .mean()
                    .reset_index(level=0, drop=True)
                )
        
        logger.debug(f"Calculated rolling averages for {len(columns)} features")
        
        return df
    
    def create_elo_ratings(
        self,
        df: pd.DataFrame,
        k_factor: float = 32,
        initial_rating: float = 1500
    ) -> pd.DataFrame:
        """
        Calcule les ratings ELO pour chaque joueur.
        
        Args:
            df: DataFrame avec les matchs triés par date
            k_factor: Facteur K d'ELO (vitesse d'adaptation)
            initial_rating: Rating initial pour nouveaux joueurs
        
        Returns:
            DataFrame avec colonnes ELO ajoutées
        """
        df = df.copy()
        df = df.sort_values('tourney_date')
        
        # Dictionnaire des ratings ELO par joueur
        elo_ratings = {}
        
        # Listes pour stocker les ELO au moment du match
        p1_elo_before = []
        p2_elo_before = []
        
        for idx, row in df.iterrows():
            p1 = row['P1']
            p2 = row['P2']
            result = row['result']
            
            # Obtenir ou initialiser les ELO
            elo_p1 = elo_ratings.get(p1, initial_rating)
            elo_p2 = elo_ratings.get(p2, initial_rating)
            
            # Stocker les ELO avant le match
            p1_elo_before.append(elo_p1)
            p2_elo_before.append(elo_p2)
            
            # Probabilité de victoire attendue
            expected_p1 = 1 / (1 + 10 ** ((elo_p2 - elo_p1) / 400))
            expected_p2 = 1 - expected_p1
            
            # Score réel (1 si victoire, 0 si défaite)
            actual_p1 = 1 if result == 1 else 0
            actual_p2 = 1 - actual_p1
            
            # Mise à jour des ELO
            new_elo_p1 = elo_p1 + k_factor * (actual_p1 - expected_p1)
            new_elo_p2 = elo_p2 + k_factor * (actual_p2 - expected_p2)
            
            # Sauvegarder les nouveaux ELO
            elo_ratings[p1] = new_elo_p1
            elo_ratings[p2] = new_elo_p2
        
        # Ajouter les ELO au DataFrame
        df['P1_elo'] = p1_elo_before
        df['P2_elo'] = p2_elo_before
        df['elo_diff'] = df['P1_elo'] - df['P2_elo']
        
        logger.info(f"✅ Created ELO ratings for {len(elo_ratings)} players")
        
        return df
    
    def create_head_to_head_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée des features basées sur l'historique des confrontations directes.
        
        Args:
            df: DataFrame avec les matchs
        
        Returns:
            DataFrame avec features H2H
        """
        df = df.copy()
        df = df.sort_values('tourney_date')
        
        # Dictionnaire pour stocker l'historique H2H
        h2h_wins = {}  # (p1, p2) -> nombre de victoires de p1
        
        h2h_records = []
        
        for idx, row in df.iterrows():
            p1 = row['P1']
            p2 = row['P2']
            result = row['result']
            
            # Créer une clé unique pour le H2H (ordre alphabétique)
            players_sorted = tuple(sorted([p1, p2]))
            
            # Récupérer l'historique
            if players_sorted not in h2h_wins:
                h2h_wins[players_sorted] = {p1: 0, p2: 0}
            
            p1_wins = h2h_wins[players_sorted].get(p1, 0)
            p2_wins = h2h_wins[players_sorted].get(p2, 0)
            total_matches = p1_wins + p2_wins
            
            # Calculer le ratio de victoires H2H
            if total_matches > 0:
                h2h_ratio = p1_wins / total_matches
            else:
                h2h_ratio = 0.5  # Neutre si pas d'historique
            
            h2h_records.append({
                'h2h_total_matches': total_matches,
                'h2h_p1_wins': p1_wins,
                'h2h_p2_wins': p2_wins,
                'h2h_p1_win_ratio': h2h_ratio
            })
            
            # Mettre à jour l'historique
            if result == 1:  # P1 gagne
                h2h_wins[players_sorted][p1] = h2h_wins[players_sorted].get(p1, 0) + 1
            else:  # P2 gagne
                h2h_wins[players_sorted][p2] = h2h_wins[players_sorted].get(p2, 0) + 1
        
        # Ajouter au DataFrame
        h2h_df = pd.DataFrame(h2h_records)
        df = pd.concat([df.reset_index(drop=True), h2h_df], axis=1)
        
        logger.info(f"✅ Created H2H features")
        
        return df
    
    def create_surface_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée des features basées sur la performance par surface.
        
        Args:
            df: DataFrame avec les matchs
        
        Returns:
            DataFrame avec features de performance par surface
        """
        df = df.copy()
        df = df.sort_values(['P1', 'tourney_date'])
        
        # Dictionnaires pour stocker les performances par surface
        surface_wins = {}  # (joueur, surface) -> nombre de victoires
        surface_total = {}  # (joueur, surface) -> nombre total de matchs
        
        p1_surface_wr = []
        p2_surface_wr = []
        
        for idx, row in df.iterrows():
            p1 = row['P1']
            p2 = row['P2']
            surface = row.get('surface', 'Unknown')
            result = row['result']
            
            # Clés pour P1 et P2
            key_p1 = (p1, surface)
            key_p2 = (p2, surface)
            
            # Calculer le win rate actuel de P1 sur cette surface
            p1_wins = surface_wins.get(key_p1, 0)
            p1_total = surface_total.get(key_p1, 0)
            p1_wr = p1_wins / p1_total if p1_total > 0 else 0.5
            
            # Calculer le win rate actuel de P2 sur cette surface
            p2_wins = surface_wins.get(key_p2, 0)
            p2_total = surface_total.get(key_p2, 0)
            p2_wr = p2_wins / p2_total if p2_total > 0 else 0.5
            
            p1_surface_wr.append(p1_wr)
            p2_surface_wr.append(p2_wr)
            
            # Mettre à jour les compteurs
            surface_total[key_p1] = surface_total.get(key_p1, 0) + 1
            surface_total[key_p2] = surface_total.get(key_p2, 0) + 1
            
            if result == 1:  # P1 gagne
                surface_wins[key_p1] = surface_wins.get(key_p1, 0) + 1
            else:  # P2 gagne
                surface_wins[key_p2] = surface_wins.get(key_p2, 0) + 1
        
        # Ajouter au DataFrame
        df['P1_surface_win_rate'] = p1_surface_wr
        df['P2_surface_win_rate'] = p2_surface_wr
        df['surface_wr_diff'] = df['P1_surface_win_rate'] - df['P2_surface_win_rate']
        
        logger.info(f"✅ Created surface performance features")
        
        return df
    
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée des features temporelles.
        
        Args:
            df: DataFrame avec colonne 'tourney_date'
        
        Returns:
            DataFrame avec features temporelles
        """
        df = df.copy()
        
        if 'tourney_date' in df.columns:
            df['year'] = df['tourney_date'].dt.year
            df['month'] = df['tourney_date'].dt.month
            df['day_of_year'] = df['tourney_date'].dt.dayofyear
            
            logger.debug("Created time features")
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline complet de feature engineering.
        
        Args:
            df: DataFrame préprocessé
        
        Returns:
            DataFrame avec features engineered
        """
        logger.info("Starting feature engineering...")
        
        # Colonnes pour les moyennes glissantes
        stat_columns = [
            'P1_rank', 'P1_rank_pts', 'P2_rank', 'P2_rank_pts',
            'P1_ace', 'P1_df', 'P1_svpt', 'P1_1stIn', 'P1_1stWon', 'P1_2ndWon',
            'P1_SvGms', 'P1_bpSaved', 'P1_bpFaced',
            'P2_ace', 'P2_df', 'P2_svpt', 'P2_1stIn', 'P2_1stWon', 'P2_2ndWon',
            'P2_SvGms', 'P2_bpSaved', 'P2_bpFaced'
        ]
        
        # Vérifier quelles colonnes existent
        stat_columns = [col for col in stat_columns if col in df.columns]
        
        # Appliquer les transformations
        df = self.calculate_rolling_stats(df, stat_columns)
        df = self.create_elo_ratings(df)
        df = self.create_head_to_head_features(df)
        df = self.create_surface_performance_features(df)
        df = self.create_time_features(df)
        
        # Trier par date
        df = df.sort_values('tourney_date').reset_index(drop=True)
        
        logger.success(f"✅ Feature engineering complete: {len(df.columns)} features")
        
        return df
