"""
Module de preprocessing des données ATP.
Nettoie et transforme les données brutes en données exploitables.
"""
from typing import List, Optional
import numpy as np
import pandas as pd
from loguru import logger

from ..utils.config import config


class ATPDataPreprocessor:
    """Préprocesseur pour les données de matchs ATP."""
    
    def __init__(self):
        self.config = config
        self.location_mapping = config.location_mapping
        self.allowed_tournaments = config.allowed_tournaments
        self.columns_to_drop = config.columns_to_drop
        self.min_matches = config.min_matches_per_player
    
    def clean_davis_cup(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Supprime les matchs de Davis Cup.
        
        Args:
            df: DataFrame brut
        
        Returns:
            DataFrame nettoyé
        """
        initial_count = len(df)
        davis_cup_count = df['tourney_name'].str.startswith('Davis Cup', na=False).sum()
        
        df_clean = df[~df['tourney_name'].str.startswith('Davis Cup', na=False)].copy()
        
        logger.info(
            f"Removed {davis_cup_count:,} Davis Cup matches "
            f"({initial_count:,} → {len(df_clean):,})"
        )
        
        return df_clean
    
    def add_location_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajoute une colonne 'Location' basée sur le nom du tournoi.
        
        Args:
            df: DataFrame avec colonne 'tourney_name'
        
        Returns:
            DataFrame avec colonne 'Location'
        """
        df = df.copy()
        df['Location'] = df['tourney_name'].replace(self.location_mapping)
        
        logger.debug(f"Added Location column with {df['Location'].nunique()} unique cities")
        
        return df
    
    def filter_tournaments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtre pour ne garder que les tournois autorisés.
        
        Args:
            df: DataFrame avec données de tournois
        
        Returns:
            DataFrame filtré
        """
        initial_count = len(df)
        df_filtered = df[df['tourney_name'].isin(self.allowed_tournaments)].copy()
        
        logger.info(
            f"Filtered to allowed tournaments: "
            f"{initial_count:,} → {len(df_filtered):,} matches"
        )
        
        return df_filtered
    
    def drop_unnecessary_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Supprime les colonnes inutiles.
        
        Args:
            df: DataFrame
        
        Returns:
            DataFrame avec colonnes supprimées
        """
        cols_to_drop = [col for col in self.columns_to_drop if col in df.columns]
        
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            logger.debug(f"Dropped {len(cols_to_drop)} columns")
        
        return df
    
    def convert_date_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convertit la colonne de date au format datetime.
        
        Args:
            df: DataFrame avec colonne 'tourney_date'
        
        Returns:
            DataFrame avec date convertie
        """
        df = df.copy()
        
        if 'tourney_date' in df.columns:
            df['tourney_date'] = pd.to_datetime(
                df['tourney_date'],
                format='%Y%m%d',
                errors='coerce'
            )
            logger.debug("Converted tourney_date to datetime")
        
        return df
    
    def rename_player_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renomme les colonnes joueurs en format P1/P2.
        
        Args:
            df: DataFrame avec colonnes winner/loser
        
        Returns:
            DataFrame avec colonnes renommées
        """
        df = df.copy()
        
        # Mapping des colonnes
        winner_to_p1 = {
            'winner_id': 'P1_id',
            'winner_name': 'P1',
            'winner_hand': 'P1_hand',
            'winner_ht': 'P1_ht',
            'winner_ioc': 'P1_ioc',
            'winner_age': 'P1_age',
            'w_ace': 'P1_ace',
            'w_df': 'P1_df',
            'w_svpt': 'P1_svpt',
            'w_1stIn': 'P1_1stIn',
            'w_1stWon': 'P1_1stWon',
            'w_2ndWon': 'P1_2ndWon',
            'w_SvGms': 'P1_SvGms',
            'w_bpSaved': 'P1_bpSaved',
            'w_bpFaced': 'P1_bpFaced',
            'winner_rank': 'P1_rank',
            'winner_rank_points': 'P1_rank_pts',
        }
        
        loser_to_p2 = {
            'loser_id': 'P2_id',
            'loser_name': 'P2',
            'loser_hand': 'P2_hand',
            'loser_ht': 'P2_ht',
            'loser_ioc': 'P2_ioc',
            'loser_age': 'P2_age',
            'l_ace': 'P2_ace',
            'l_df': 'P2_df',
            'l_svpt': 'P2_svpt',
            'l_1stIn': 'P2_1stIn',
            'l_1stWon': 'P2_1stWon',
            'l_2ndWon': 'P2_2ndWon',
            'l_SvGms': 'P2_SvGms',
            'l_bpSaved': 'P2_bpSaved',
            'l_bpFaced': 'P2_bpFaced',
            'loser_rank': 'P2_rank',
            'loser_rank_points': 'P2_rank_pts',
        }
        
        # Appliquer les renommages
        all_renames = {**winner_to_p1, **loser_to_p2}
        cols_to_rename = {k: v for k, v in all_renames.items() if k in df.columns}
        
        df = df.rename(columns=cols_to_rename)
        logger.debug(f"Renamed {len(cols_to_rename)} player columns")
        
        return df
    
    def create_result_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée une colonne 'result' (1 si P1 gagne, -1 si P2 gagne).
        
        Args:
            df: DataFrame avec colonnes P1 et P2
        
        Returns:
            DataFrame avec colonne 'result'
        """
        df = df.copy()
        df['result'] = 1  # P1 est toujours le vainqueur initialement
        
        logger.debug("Created result column")
        
        return df
    
    def augment_with_reversed_matches(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Double le dataset en inversant les rôles P1/P2.
        Permet d'équilibrer les données et d'avoir plus d'exemples.
        
        Args:
            df: DataFrame avec matchs
        
        Returns:
            DataFrame augmenté
        """
        initial_count = len(df)
        
        # Créer une copie inversée
        df_reversed = df.copy()
        
        # Colonnes P1 à échanger avec P2
        p1_cols = [col for col in df.columns if col.startswith('P1')]
        p2_cols = [col for col in df.columns if col.startswith('P2')]
        
        # Vérifier qu'on a le même nombre
        if len(p1_cols) != len(p2_cols):
            logger.warning("Mismatch in P1/P2 columns count!")
        
        # Inverser les colonnes
        for p1_col in p1_cols:
            p2_col = p1_col.replace('P1', 'P2')
            if p2_col in df_reversed.columns:
                df_reversed[p1_col], df_reversed[p2_col] = (
                    df_reversed[p2_col].values,
                    df_reversed[p1_col].values
                )
        
        # Inverser le résultat
        df_reversed['result'] = -1
        
        # Combiner
        df_augmented = pd.concat([df, df_reversed], ignore_index=True)
        df_augmented = df_augmented.sort_values('tourney_date').reset_index(drop=True)
        
        logger.info(f"Augmented dataset: {initial_count:,} → {len(df_augmented):,} matches")
        
        return df_augmented
    
    def filter_players_by_match_count(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtre pour ne garder que les joueurs avec assez de matchs.
        
        Args:
            df: DataFrame avec colonne P1
        
        Returns:
            DataFrame filtré
        """
        initial_count = len(df)
        
        # Compter les matchs par joueur
        player_counts = df['P1'].value_counts()
        valid_players = player_counts[player_counts >= self.min_matches].index
        
        # Filtrer
        df_filtered = df[df['P1'].isin(valid_players)].copy()
        
        logger.info(
            f"Filtered players with >={self.min_matches} matches: "
            f"{len(player_counts)} → {len(valid_players)} players, "
            f"{initial_count:,} → {len(df_filtered):,} matches"
        )
        
        return df_filtered
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gère les valeurs manquantes.
        
        Args:
            df: DataFrame
        
        Returns:
            DataFrame nettoyé
        """
        initial_count = len(df)
        
        # Supprimer les lignes avec des valeurs manquantes critiques
        df_clean = df.dropna(subset=['P1', 'P2', 'result'])
        
        removed = initial_count - len(df_clean)
        if removed > 0:
            logger.info(f"Removed {removed:,} rows with missing critical values")
        
        return df_clean
    
    def preprocess(
        self,
        df: pd.DataFrame,
        augment_data: bool = True
    ) -> pd.DataFrame:
        """
        Pipeline complet de preprocessing.
        
        Args:
            df: DataFrame brut
            augment_data: Activer l'augmentation de données
        
        Returns:
            DataFrame préprocessé
        """
        logger.info("Starting preprocessing pipeline...")
        
        # Étapes de preprocessing
        df = self.clean_davis_cup(df)
        df = self.add_location_column(df)
        df = self.convert_date_column(df)
        df = self.filter_tournaments(df)
        df = self.rename_player_columns(df)
        df = self.drop_unnecessary_columns(df)
        df = self.create_result_column(df)
        df = self.handle_missing_values(df)
        
        
        # Augmentation optionnelle
        if augment_data:
            df = self.augment_with_reversed_matches(df)
        
        df = self.filter_players_by_match_count(df)
        
        logger.success(f"✅ Preprocessing complete: {len(df):,} matches ready")
        
        return df
