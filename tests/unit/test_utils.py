from src.utils.logger import setup_logging


def test_setup_logging_does_not_crash(tmp_path):
    log_file = tmp_path / "test.log"

    setup_logging(
        log_level="INFO",
        log_file=str(log_file),
    )

    assert log_file.exists()