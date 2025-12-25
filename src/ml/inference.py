"""
Module d'inférence pour la prédiction de matchs ATP.

Charge automatiquement le modèle daté le plus récent (model_YYYYMMDD.pkl)
ou model.pkl si aucun modèle daté n'existe.
"""
import joblib
import pandas as pd
from pathlib import Path
from loguru import logger

from ..utils.config import get_config
config = get_config()


class MatchPredictor:
    """Classe pour prédire les résultats de matchs ATP."""
    
    def __init__(self):
        """Initialise le prédicteur et charge le modèle."""
        self.model = self._load_model()
        self.model_path = None  # Sera défini par _load_model()
        
    def _find_latest_model(self, models_dir: Path) -> Path:
        """
        Trouve le modèle le plus récent à charger.
        
        Priorité:
        1. Modèles datés (model_YYYYMMDD.pkl) - prend le plus récent
        2. model.pkl (fallback)
        
        Args:
            models_dir: Dossier des modèles
        
        Returns:
            Chemin du modèle à charger
        
        Raises:
            FileNotFoundError: Si aucun modèle n'est trouvé
        """
        # 1. Chercher les modèles datés
        dated_models = sorted(models_dir.glob("model_*.pkl"))
        
        if dated_models:
            # Prendre le plus récent (tri alphabétique sur YYYYMMDD)
            latest_model = dated_models[-1]
            logger.info(f"📅 Modèle daté trouvé: {latest_model.name}")
            return latest_model
        
        # 2. Fallback sur model.pkl
        fallback_model = models_dir / "model.pkl"
        if fallback_model.exists():
            logger.info(f"📁 Modèle générique trouvé: model.pkl")
            return fallback_model
        
        # 3. Aucun modèle trouvé
        raise FileNotFoundError(
            f"❌ Aucun modèle trouvé dans {models_dir}\n"
            f"Recherché: model_YYYYMMDD.pkl ou model.pkl\n"
            f"Exécutez d'abord: python -m src.ml.train_model"
        )
    
    def _load_model(self):
        """
        Charge le modèle ML depuis le disque.
        
        Returns:
            Modèle chargé
        """
        try:
            models_dir = config.data_paths["models"]
            
            # Trouver le modèle le plus récent
            model_path = self._find_latest_model(models_dir)
            self.model_path = model_path
            
            # Charger le modèle
            logger.info(f"🔵 Chargement du modèle: {model_path}")
            model = joblib.load(model_path)
            
            logger.success(f"✅ Modèle chargé avec succès: {model_path.name}")
            
            return model
            
        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
            raise
    
    def predict_proba(self, player1: str, player2: str) -> float:
        """
        Prédit la probabilité de victoire du player1 contre player2.
        
        Args:
            player1: Nom du joueur 1
            player2: Nom du joueur 2
        
        Returns:
            Probabilité de victoire du player1 (entre 0 et 1)
        
        Raises:
            ValueError: Si l'un des joueurs n'est pas dans le dataset
        """
        # TODO: Implémenter la logique de prédiction
        # Pour l'instant, retourne une probabilité basique basée sur ELO
        
        try:
            # Charger le dataset gold
            gold_path = config.data_paths["gold"] / "atp_matches_gold.csv"
            df = pd.read_csv(gold_path)
            
            # Récupérer les ELO des joueurs
            p1_data = df[df['P1'] == player1].sort_values('tourney_date', ascending=False).head(1)
            p2_data = df[df['P1'] == player2].sort_values('tourney_date', ascending=False).head(1)
            
            if p1_data.empty:
                raise ValueError(f"Joueur '{player1}' non trouvé dans le dataset")
            if p2_data.empty:
                raise ValueError(f"Joueur '{player2}' non trouvé dans le dataset")
            
            p1_elo = p1_data['P1_elo'].iloc[0] if 'P1_elo' in p1_data.columns else 1500
            p2_elo = p2_data['P1_elo'].iloc[0] if 'P1_elo' in p2_data.columns else 1500
            
            # Formule ELO standard
            prob_p1 = 1 / (1 + 10 ** ((p2_elo - p1_elo) / 400))
            
            logger.debug(f"Prédiction: {player1} vs {player2}")
            logger.debug(f"ELO: {p1_elo:.0f} vs {p2_elo:.0f}")
            logger.debug(f"Probabilité: {prob_p1:.2%}")
            
            return prob_p1
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la prédiction: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """
        Retourne les informations sur le modèle chargé.
        
        Returns:
            Dictionnaire avec les infos du modèle
        """
        if self.model_path is None:
            return {"error": "Aucun modèle chargé"}
        
        return {
            "model_name": self.model_path.name,
            "model_path": str(self.model_path),
            "model_size_mb": self.model_path.stat().st_size / (1024 * 1024),
            "model_type": type(self.model).__name__
        }


# Instance globale pour le cache
_predictor_instance = None


def get_predictor() -> MatchPredictor:
    """
    Retourne une instance singleton du prédicteur.
    Utilisé par Streamlit pour le cache.
    
    Returns:
        Instance du MatchPredictor
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = MatchPredictor()
    
    return _predictor_instance


if __name__ == "__main__":
    # Test du module
    predictor = MatchPredictor()
    
    print("\n📊 Informations sur le modèle:")
    info = predictor.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n🎾 Test de prédiction:")
    try:
        prob = predictor.predict_proba("Rafael Nadal", "Novak Djokovic")
        print(f"  Rafael Nadal vs Novak Djokovic: {prob:.2%}")
    except ValueError as e:
        print(f"  ⚠️  {e}")