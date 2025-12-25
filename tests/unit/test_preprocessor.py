import pandas as pd
from src.data.preprocessor import ATPDataPreprocessor


def test_filter_tournaments_keeps_only_allowed():
    df = pd.DataFrame({
        "tourney_name": ["Australian Open", "Random Cup"],
        "tourney_date": [20240101, 20240102],
        "winner_id": [1, 2],
        "loser_id": [3, 4],
    })

    preprocessor = ATPDataPreprocessor()
    preprocessor.allowed_tournaments = ["Australian Open"]

    filtered = preprocessor.filter_tournaments(df)

    assert len(filtered) == 1
    assert filtered.iloc[0]["tourney_name"] == "Australian Open"

    

def test_drop_unnecessary_columns():
    df = pd.DataFrame({
        "winner_id": [1],
        "loser_id": [2],
        "useless_col": [999],
    })

    preprocessor = ATPDataPreprocessor()
    preprocessor.columns_to_drop = ["useless_col"]

    clean_df = preprocessor.drop_unnecessary_columns(df)

    assert "useless_col" not in clean_df.columns
    assert "winner_id" in clean_df.columns