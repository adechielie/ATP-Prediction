import sys
from pathlib import Path
import pytest
import pandas as pd

# Ajouter la racine du projet au PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def minimal_atp_df():
    return pd.DataFrame({
        "tourney_name": ["Australian Open", "Wimbledon"],
        "tourney_date": [20240101, 20240102],
        "tourney_level": ["G", "A"],
        "winner_id": [1, 2],
        "winner_name": ["Player A", "Player B"],
        "loser_id": [3, 4],
        "loser_name": ["Player C", "Player D"],
    })

@pytest.fixture
def minimal_config():
    """Config minimale simulée."""
    return {
        "allowed_tournaments": ["G", "A"],
        "min_matches_per_player": 1,
    }
