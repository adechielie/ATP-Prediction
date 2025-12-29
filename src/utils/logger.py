"""
Module de logging configuré avec loguru.
"""
import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_level: str = "INFO", log_file: str = "atp_prediction.log") -> None:
    """
    Configure le système de logging.
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nom du fichier de log
    """
    # Supprimer le handler par défaut
    logger.remove()
    
    # Ajouter un handler console avec couleurs
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
""" # Ajouter un handler fichier
    log_path = Path(__file__).parent.parent.parent / "logs" / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    
    logger.info(f"Logging configured - Level: {log_level}, File: {log_path}")


# Configuration par défaut
setup_logging()"""
