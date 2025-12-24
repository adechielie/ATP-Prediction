"""
Module de gestion de la configuration.
Charge et valide les paramètres depuis config.yaml
"""
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from loguru import logger


class Config:
    """Classe singleton pour gérer la configuration de l'application."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Charge la configuration depuis le fichier YAML."""
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        logger.info(f"Configuration loaded from {config_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration (supporte les chemins avec '.')
            default: Valeur par défaut si la clé n'existe pas
        
        Returns:
            La valeur de configuration
        
        Example:
            >>> config = Config()
            >>> config.get('model.algorithm')
            'gradient_boosting'
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def data_paths(self) -> Dict[str, Path]:
        """Retourne les chemins de données configurés."""
        base_path = Path(__file__).parent.parent.parent
        paths = self.get('data.paths', {})
        return {k: base_path / v for k, v in paths.items()}
    
    @property
    def atp_base_url(self) -> str:
        """URL de base pour les données ATP."""
        return self.get('data.sources.atp_github.base_url', '')
    
    @property
    def years_range(self) -> List[int]:
        """Plage d'années pour les données ATP."""
        years = self.get('data.sources.atp_github.years_range', [2000, 2025])
        return list(range(years[0], years[1]))
    
    @property
    def allowed_tournaments(self) -> List[str]:
        """Liste des tournois autorisés."""
        return self.get('tournaments.allowed', [])
    
    @property
    def location_mapping(self) -> Dict[str, str]:
        """Mapping des noms de tournois vers les villes."""
        return self.get('location_mapping', {})
    
    @property
    def min_matches_per_player(self) -> int:
        """Nombre minimum de matchs par joueur."""
        return self.get('preprocessing.min_matches_per_player', 10)
    
    @property
    def rolling_window(self) -> int:
        """Fenêtre pour les moyennes glissantes."""
        return self.get('preprocessing.rolling_window', 5)
    
    @property
    def columns_to_drop(self) -> List[str]:
        """Colonnes à supprimer lors du preprocessing."""
        return self.get('preprocessing.columns_to_drop', [])
    
    @property
    def model_config(self) -> Dict[str, Any]:
        """Configuration du modèle."""
        return self.get('model', {})
    
    def __repr__(self) -> str:
        return f"Config(keys={list(self._config.keys())})"


# Instance globale
config = Config()
