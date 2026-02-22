"""
Collecteur de données ATP 2025 depuis TML Database avec harmonisation.
Convertit la structure TML vers la structure Jeff Sackmann (2024).
"""
import pandas as pd
from pathlib import Path
from loguru import logger

from src.utils.config import get_config

config = get_config()


class TMLDataCollector:
    """Collecte et harmonise les données ATP 2025 depuis TML Database."""
    
    def __init__(self):
        self.base_url = config.get("data.sources.tml_database.base_url")
        self.year = config.get("data.sources.tml_database.year")
        self.raw_path = config.data_paths["raw"]
        self.raw_path.mkdir(parents=True, exist_ok=True)
    
    def harmonize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Harmonise les colonnes TML 2025 vers le format Jeff Sackmann 2024.
        
        Différences à corriger:
        - TML 2025 a: P1, P2, indoor, year, winner_rank, winner_rank_points
        - Jeff 2024 a: winner_name, loser_name (pas de P1/P2, indoor, year)
        - Position des colonnes winner_rank/loser_rank différente
        
        Args:
            df: DataFrame brut de TML
        
        Returns:
            DataFrame harmonisé au format Jeff Sackmann
        """
        logger.info("🔧 Harmonisation des colonnes TML → Jeff Sackmann")
        
        df_harmonized = df.copy()
        
        # 1. Renommer P1 → winner_name, P2 → loser_name
        if 'P1' in df_harmonized.columns:
            df_harmonized.rename(columns={'P1': 'winner_name'}, inplace=True)
            logger.debug("  ✅ P1 → winner_name")
        
        if 'P2' in df_harmonized.columns:
            df_harmonized.rename(columns={'P2': 'loser_name'}, inplace=True)
            logger.debug("  ✅ P2 → loser_name")
        
        # 2. Supprimer les colonnes spécifiques à TML
        columns_to_drop = []
        
        if 'indoor' in df_harmonized.columns:
            columns_to_drop.append('indoor')
            logger.debug("  🗑️  Suppression: indoor")
        
        if 'year' in df_harmonized.columns:
            columns_to_drop.append('year')
            logger.debug("  🗑️  Suppression: year")
        
        if columns_to_drop:
            df_harmonized.drop(columns=columns_to_drop, inplace=True)
        
        # 3. Réorganiser les colonnes pour correspondre exactement à Jeff Sackmann
        # Ordre exact de Jeff Sackmann (2024):
        target_columns = [
            'tourney_id', 'tourney_name', 'surface', 'draw_size', 'tourney_level',
            'tourney_date', 'match_num', 'winner_id', 'winner_seed', 'winner_entry',
            'winner_name', 'winner_hand', 'winner_ht', 'winner_ioc', 'winner_age',
            'loser_id', 'loser_seed', 'loser_entry', 'loser_name', 'loser_hand',
            'loser_ht', 'loser_ioc', 'loser_age', 'score', 'best_of', 'round',
            'minutes', 'w_ace', 'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon',
            'w_2ndWon', 'w_SvGms', 'w_bpSaved', 'w_bpFaced', 'l_ace', 'l_df',
            'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_SvGms', 'l_bpSaved',
            'l_bpFaced', 'winner_rank', 'winner_rank_points', 'loser_rank',
            'loser_rank_points'
        ]
        
        # Vérifier que toutes les colonnes nécessaires sont présentes
        missing_columns = [col for col in target_columns if col not in df_harmonized.columns]
        
        if missing_columns:
            logger.warning(f"⚠️  Colonnes manquantes (seront NaN): {missing_columns}")
            for col in missing_columns:
                df_harmonized[col] = None
        
        # Réorganiser dans le bon ordre
        df_harmonized = df_harmonized[target_columns]
        
        logger.success(f"✅ Harmonisation terminée: {len(df_harmonized)} matchs, {len(df_harmonized.columns)} colonnes")
        
        return df_harmonized
    
    def fetch_2025(self) -> pd.DataFrame:
        """
        Télécharge et harmonise les données ATP 2025 depuis TML.
        
        Returns:
            DataFrame harmonisé au format Jeff Sackmann
        """
        url = f"{self.base_url}2025.csv"
        logger.info(f"📥 Downloading ATP {self.year} data from TML Database")
        logger.debug(f"URL: {url}")
        
        try:
            # Télécharger
            df = pd.read_csv(url)
            logger.info(f"✅ Downloaded: {len(df)} matchs, {len(df.columns)} colonnes")
            
            # Harmoniser
            df_harmonized = self.harmonize_columns(df)
            
            # Sauvegarder
            output_path = self.raw_path / "atp_matches_2025.csv"
            df_harmonized.to_csv(output_path, index=False)
            
            logger.success(f"💾 Saved harmonized ATP 2025 data to {output_path}")
            
            return df_harmonized
        
        except Exception as e:
            logger.error(f"❌ Error downloading ATP 2025 data: {e}")
            raise
    
    def load_from_disk(self) -> pd.DataFrame:
        """
        Charge les données ATP 2025 depuis le disque.
        
        Returns:
            DataFrame
        """
        file_path = self.raw_path / "atp_matches_2025.csv"
        
        if not file_path.exists():
            raise FileNotFoundError(f"❌ File not found: {file_path}")
        
        df = pd.read_csv(file_path)
        logger.info(f"📂 Loaded ATP 2025 from disk: {len(df)} matchs")
        
        return df
    
    def get_or_fetch_data(self, force_download: bool = False) -> pd.DataFrame:
        """
        Récupère les données depuis le disque ou télécharge si nécessaire.
        
        Args:
            force_download: Forcer le téléchargement
        
        Returns:
            DataFrame ATP 2025
        """
        if force_download:
            return self.fetch_2025()
        
        try:
            return self.load_from_disk()
        except FileNotFoundError:
            logger.info("No local ATP 2025 data found, downloading...")
            return self.fetch_2025()


if __name__ == "__main__":
    # Test du module
    collector = TMLDataCollector()
    df = collector.fetch_2025()
    
    print("\n" + "=" * 70)
    print("✅ ATP 2025 DATA HARMONIZED")
    print("=" * 70)
    print(f"Shape: {df.shape}")
    print(f"\nColumns ({len(df.columns)}):")
    print(df.columns.tolist())
    print(f"\nFirst match:")
    print(df.head(1).T)
    print("=" * 70)