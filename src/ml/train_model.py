"""
Script d'entraînement du modèle ATP.

Sauvegarde le modèle avec la date du jour: model_YYYYMMDD.pkl
Si un modèle existe déjà pour ce jour, il est écrasé.

Usage:
    python -m src.ml.train_model
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from loguru import logger
from pathlib import Path
from datetime import datetime

from ..utils.config import config


def train_model():
    """Fonction principale d'entraînement."""
    
    logger.info("=" * 70)
    logger.info("🎾 ENTRAÎNEMENT DU MODÈLE ATP")
    logger.info("=" * 70)
    
    # === CHARGEMENT DES DONNÉES ===
    logger.info("🔵 Loading GOLD dataset...")
    gold_path = config.data_paths["gold"] / "atp_matches_gold.csv"
    
    if not gold_path.exists():
        raise FileNotFoundError(f"❌ Dataset GOLD non trouvé: {gold_path}")
    
    df = pd.read_csv(gold_path)
    logger.info(f"Dataset loaded: {df.shape}")

    # === IDENTIFIER LA COLONNE TARGET ===
    if "result" in df.columns:
        target_col = "result"
    elif "winner" in df.columns:
        target_col = "winner"
    else:
        raise ValueError(f"❌ No target column found. Available columns: {df.columns.tolist()}")
    
    logger.info(f"📊 Using target column: '{target_col}'")

    # === PRÉPARATION FEATURES / TARGET ===
    y = df[target_col]
    X = df.drop(target_col, axis=1)
    
    # Enlever les colonnes non-numériques
    non_numeric_cols = X.select_dtypes(exclude=['number']).columns.tolist()
    if non_numeric_cols:
        logger.warning(f"⚠️ Dropping non-numeric columns: {non_numeric_cols}")
        X = X.select_dtypes(include=['number'])
    
    # Gérer les valeurs manquantes
    if X.isnull().any().any():
        logger.warning("⚠️ Missing values detected. Filling with 0...")
        X = X.fillna(0)
    
    logger.info(f"✅ Features shape: {X.shape}")
    logger.info(f"✅ Target distribution:\n{y.value_counts()}")

    # === TRAIN / TEST SPLIT ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.model_config["test_size"], random_state=42
    )
    
    logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")

    # === CONFIGURATION DU MODÈLE ===
    algo = config.model_config["algorithm"]
    params = config.model_config["hyperparameters"][algo]

    logger.info(f"🔧 Training model: {algo}")
    logger.info(f"Hyperparameters: {params}")

    # === SÉLECTION DU MODÈLE ===
    if algo == "gradient_boosting":
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(**params)

    elif algo == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(**params)

    elif algo == "logistic_regression":
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(**params)

    elif algo == "knn":
        from sklearn.neighbors import KNeighborsClassifier
        model = KNeighborsClassifier(**params)

    else:
        raise ValueError(f"Unknown algorithm: {algo}")

    # === ENTRAÎNEMENT ===
    logger.info("🚀 Training started...")
    start_time = datetime.now()
    
    model.fit(X_train, y_train)
    
    training_time = (datetime.now() - start_time).total_seconds()
    logger.success(f"✅ Training completed in {training_time:.1f}s")

    # === ÉVALUATION ===
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    logger.success(f"🎯 Model accuracy: {acc:.2%}")

    # === SAUVEGARDE AVEC DATE DU JOUR ===
    models_dir = config.data_paths["models"]
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Nom avec la date du jour: model_YYYYMMDD.pkl
    date_str = datetime.now().strftime("%Y%m%d")
    model_filename = f"model_{date_str}.pkl"
    model_path = models_dir / model_filename
    
    # Si un modèle du jour existe déjà, l'écraser
    if model_path.exists():
        logger.warning(f"⚠️  Modèle du jour existe déjà, écrasement: {model_filename}")
    
    joblib.dump(model, model_path)
    
    size_mb = model_path.stat().st_size / (1024 * 1024)
    logger.success(f"💾 Model saved: {model_filename} ({size_mb:.2f} MB)")
    
    # === RÉSUMÉ ===
    logger.info("=" * 70)
    logger.success("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
    logger.info(f"📊 Accuracy: {acc:.2%}")
    logger.info(f"📁 Modèle: {model_path}")
    logger.info(f"⏱️  Durée: {training_time:.1f}s")
    logger.info("=" * 70)
    
    return model, acc


if __name__ == "__main__":
    train_model()