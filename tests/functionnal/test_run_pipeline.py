from src.data.preprocessor import ATPDataPreprocessor


def test_preprocess_pipeline_minimal(minimal_atp_df):
    preprocessor = ATPDataPreprocessor()

    # Neutraliser la contrainte métier pour le test
    preprocessor.min_matches = 1

    result = preprocessor.preprocess(
        minimal_atp_df,
        augment_data=False,
    )

    assert not result.empty