import pandas as pd
from pathlib import Path
from loguru import logger

from src.utils.config import get_config

config = get_config()


class TMLDataCollector:
    def __init__(self):
        self.base_url = config.get("data.sources.tml_database.base_url")
        self.year = config.get("data.sources.tml_database.year")
        self.raw_path = config.data_paths["raw"]
        self.raw_path.mkdir(parents=True, exist_ok=True)

    def fetch_2025(self) -> pd.DataFrame:
        url = f"{self.base_url}2025.csv"
        logger.info(f"TML FINAL URL = {url}") 

        logger.info(f"Downloading ATP {self.year} data from TML")

        df = pd.read_csv(url)

        # 🔧 Harmonisation minimale (EXEMPLE)
        df.rename(columns={
            "winner_name": "P1",
            "loser_name": "P2",
            "tournament": "tourney_name",
            "match_date": "tourney_date",
        }, inplace=True)

        # 🔧 Ajouter colonne année si absente
        df["year"] = self.year

        output = self.raw_path / "atp_matches_2025.csv"
        df.to_csv(output, index=False)

        logger.success(f"Saved ATP {self.year} data to {output}")

        return df

if __name__ == "__main__":
    collector = TMLDataCollector()
    df = collector.fetch_2025()
    print(f"✅ ATP 2025 loaded: {df.shape}")
