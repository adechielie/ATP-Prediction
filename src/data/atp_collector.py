"""
Collecteur de données ATP depuis GitHub (Jeff Sackmann) + TML pour 2025.
"""
from typing import List, Optional
from pathlib import Path

import pandas as pd
import requests
from loguru import logger
from tqdm import tqdm

from ..utils.config import get_config
config = get_config()


class ATPDataCollector:
    """Collecte les données de matchs ATP depuis le dépôt GitHub + TML."""
    
    def __init__(self):
        self.base_url = config.atp_base_url
        self.years = config.years_range
        self.raw_path = config.data_paths['raw']
        self.raw_path.mkdir(parents=True, exist_ok=True)
    
    def fetch_year_data(self, year: int) -> Optional[pd.DataFrame]:
        """
        Récupère les données d'une année spécifique depuis Jeff Sackmann.
        
        Args:
            year: Année à récupérer
        
        Returns:
            DataFrame ou None si erreur
        """
        url = f"{self.base_url}atp_matches_{year}.csv"
        
        try:
            df = pd.read_csv(url)
            logger.debug(f"✅ Downloaded {year} data: {len(df)} matches")
            return df
        
        except Exception as e:
            logger.warning(f"⚠️  Failed to download {year}: {e}")
            return None
    
    def collect_all_years(
        self,
        years: Optional[List[int]] = None,
        save_to_disk: bool = True
    ) -> pd.DataFrame:
        """
        Collecte les données pour toutes les années spécifiées.
        
        Args:
            years: Liste des années (utilise config par défaut si None)
            save_to_disk: Sauvegarder les fichiers CSV individuels
        
        Returns:
            DataFrame concatené de toutes les années
        """
        years = years or self.years
        dfs = []
        
        logger.info(f"Collecting ATP data for years {min(years)}-{max(years)}")
        
        for year in tqdm(years, desc="Downloading years"):
            # ⛔ Jeff Sackmann n'a pas encore 2025
            if year == 2025:
                logger.info(f"Skipping {year} (will use TML data if available)")
                continue
            
            df = self.fetch_year_data(year)
            
            if df is not None:
                # Sauvegarder individuellement si demandé
                if save_to_disk:
                    file_path = self.raw_path / f"atp_matches_{year}.csv"
                    df.to_csv(file_path, index=False)
                    logger.debug(f"Saved {file_path}")
                
                dfs.append(df)
        
        # 🔵 Ajouter 2025 depuis TML si présent (déjà harmonisé)
        tml_2025_path = self.raw_path / "atp_matches_2025.csv"
        
        if tml_2025_path.exists():
            logger.info("📥 Adding ATP 2025 data from TML Database (harmonized)")
            df_2025 = pd.read_csv(tml_2025_path)
            logger.info(f"  ✅ Loaded {len(df_2025)} matches from 2025")
            dfs.append(df_2025)
        elif 2025 in years:
            logger.warning("⚠️  ATP 2025 data not found in raw/. Run TMLDataCollector first.")
        
        # Concaténer tous les DataFrames
        if not dfs:
            raise ValueError("No data collected!")
        
        combined_df = pd.concat(dfs, ignore_index=True)
        
        logger.success(
            f"✅ Collected {len(combined_df):,} matches from {len(dfs)} year(s)"
        )
        
        return combined_df
    
    def load_from_disk(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Charge les données depuis les fichiers locaux.
        
        Args:
            years: Liste des années à charger
        
        Returns:
            DataFrame combiné
        """
        years = years or self.years
        dfs = []
        
        for year in years:
            file_path = self.raw_path / f"atp_matches_{year}.csv"
            
            if file_path.exists():
                df = pd.read_csv(file_path)
                dfs.append(df)
                logger.debug(f"Loaded {year}: {len(df)} matches")
            else:
                logger.warning(f"File not found: {file_path}")
        
        if not dfs:
            raise FileNotFoundError("No local data files found!")
        
        combined_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Loaded {len(combined_df):,} matches from disk ({len(dfs)} years)")
        
        return combined_df
    
    def get_or_fetch_data(
        self,
        force_download: bool = False
    ) -> pd.DataFrame:
        """
        Récupère les données depuis le disque ou télécharge si nécessaire.
        
        Args:
            force_download: Forcer le téléchargement même si les fichiers existent
        
        Returns:
            DataFrame des matchs ATP
        """
        if force_download:
            return self.collect_all_years()
        
        try:
            return self.load_from_disk()
        except FileNotFoundError:
            logger.info("No local data found, downloading...")
            return self.collect_all_years()