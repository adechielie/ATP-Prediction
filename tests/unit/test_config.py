from src.utils.config import get_config
config = get_config()

def test_config_loaded():
    assert config is not None


def test_allowed_tournaments_not_empty():
    assert isinstance(config.allowed_tournaments, list)
    assert len(config.allowed_tournaments) > 0
