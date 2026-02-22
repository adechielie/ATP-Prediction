"""
Script principal pour le pipeline complet ATP Prediction.
Collecte les données 2000-2024 (Jeff Sackmann) + 2025 (TML Database harmonisé).
"""
import argparse
from pathlib import Path

from src.data.atp_collector import ATPDataCollector
from src.data.tml_collector import TMLDataCollector
from src.data.climate_collector import ClimateDataCollector
from src.data.preprocessor import ATPDataPreprocessor
from src.features.feature_engineer import ATPFeatureEngineer
from src.utils.logger import logger, setup_logging

setup_logging()


def main(
    force_download: bool = False,
    save_bronze: bool = True,
    save_silver: bool = True,
    save_gold: bool = True
):
    """
    Pipeline complet de préparation des données.
    
    Args:
        force_download: Forcer le téléchargement des données
        save_bronze: Sauvegarder les données bronze
        save_silver: Sauvegarder les données silver
        save_gold: Sauvegarder les données gold
    """
    logger.info("=" * 80)
    logger.info("🚀 ATP PREDICTION - PIPELINE DÉMARRÉ")
    logger.info("=" * 80)
    
    # ==========================================
    # ÉTAPE 1 : COLLECTE DES DONNÉES (BRONZE)
    # ==========================================
    logger.info("\n📥 ÉTAPE 1/4 : Collecte des données ATP...")
    
    # 🆕 SOUS-ÉTAPE 1A : Collecter 2025 depuis TML (harmonisation automatique)
    logger.info("\n📥 1A : Collecte ATP 2025 depuis TML Database...")
    try:
        tml_collector = TMLDataCollector()
        tml_2025 = tml_collector.get_or_fetch_data(force_download=force_download)
        logger.success(f"✅ ATP 2025 (TML) : {len(tml_2025):,} matchs (harmonisé)")
    except Exception as e:
        logger.warning(f"⚠️  Impossible de charger ATP 2025 depuis TML: {e}")
        logger.info("Continuation sans données 2025")
    
    # 🆕 SOUS-ÉTAPE 1B : Collecter 2000-2024 depuis Jeff Sackmann + charger 2025 harmonisé
    logger.info("\n📥 1B : Collecte ATP 2000-2024 depuis Jeff Sackmann...")
    atp_collector = ATPDataCollector()
    atp_data = atp_collector.get_or_fetch_data(force_download=force_download)
    
    logger.success(f"✅ Données ATP totales : {len(atp_data):,} matchs")
    
    # Afficher la répartition par année
    if 'tourney_date' in atp_data.columns:
        atp_data['tourney_date'] = pd.to_datetime(atp_data['tourney_date'])
        years_count = atp_data['tourney_date'].dt.year.value_counts().sort_index()
        logger.info(f"📊 Répartition : {years_count.min()} à {years_count.max()}")
        if 2025 in years_count.index:
            logger.info(f"   → 2025 : {years_count[2025]:,} matchs ✅")
    
    # Données climatiques
    logger.info("\n🌤️  1C : Collecte des données climatiques...")
    climate_collector = ClimateDataCollector()
    climate_data = climate_collector.get_or_fetch_data(force_download=force_download)
    
    logger.success(f"✅ Données climatiques : {len(climate_data):,} enregistrements")
    
    # Sauvegarder bronze
    if save_bronze:
        bronze_path = Path(__file__).parent / "data" / "bronze"
        bronze_path.mkdir(parents=True, exist_ok=True)
        
        atp_data.to_csv(bronze_path / "atp_matches_bronze.csv", index=False)
        climate_data.to_csv(bronze_path / "climate_bronze.csv", index=False)
        logger.info(f"💾 Données bronze sauvegardées dans {bronze_path}")
    
    # ==========================================
    # ÉTAPE 2 : PREPROCESSING (SILVER)
    # ==========================================
    logger.info("\n🧹 ÉTAPE 2/4 : Preprocessing des données...")
    
    preprocessor = ATPDataPreprocessor()
    clean_data = preprocessor.preprocess(atp_data, augment_data=True)
    
    # Fusionner avec les données climatiques
    logger.info("\n🔗 Fusion avec les données climatiques...")
    clean_data = clean_data.merge(
        climate_data,
        left_on=['Location', 'tourney_date'],
        right_on=['city', 'date'],
        how='left'
    )
    clean_data = clean_data.drop(columns=['city', 'date'], errors='ignore')
    
    logger.success(f"✅ Données nettoyées : {len(clean_data):,} matchs")
    
    # Sauvegarder silver
    if save_silver:
        silver_path = Path(__file__).parent / "data" / "silver"
        silver_path.mkdir(parents=True, exist_ok=True)
        
        clean_data.to_csv(silver_path / "atp_matches_silver.csv", index=False)
        logger.info(f"💾 Données silver sauvegardées dans {silver_path}")
    
    # ==========================================
    # ÉTAPE 3 : FEATURE ENGINEERING (GOLD)
    # ==========================================
    logger.info("\n⚙️  ÉTAPE 3/4 : Feature engineering...")
    
    engineer = ATPFeatureEngineer()
    features_data = engineer.engineer_features(clean_data)
    
    logger.success(f"✅ Features créées : {len(features_data.columns)} colonnes")
    
    # Sauvegarder gold
    if save_gold:
        gold_path = Path(__file__).parent / "data" / "gold"
        gold_path.mkdir(parents=True, exist_ok=True)
        
        features_data.to_csv(gold_path / "atp_matches_gold.csv", index=False)
        logger.info(f"💾 Données gold sauvegardées dans {gold_path}")
    
    # ==========================================
    # ÉTAPE 4 : RÉSUMÉ
    # ==========================================
    logger.info("\n" + "=" * 80)
    logger.info("📊 RÉSUMÉ DU PIPELINE")
    logger.info("=" * 80)
    logger.info(f"Bronze : {len(atp_data):,} matchs bruts")
    logger.info(f"Silver : {len(clean_data):,} matchs nettoyés")
    logger.info(f"Gold   : {len(features_data):,} matchs avec {len(features_data.columns)} features")
    
    # Afficher les années présentes
    if 'tourney_date' in features_data.columns:
        years = features_data['tourney_date'].dt.year.unique()
        logger.info(f"Années : {min(years)} à {max(years)} ({len(years)} années)")
    
    logger.info("=" * 80)
    logger.success("✅ PIPELINE TERMINÉ AVEC SUCCÈS")
    logger.info("=" * 80)
    
    return features_data


if __name__ == "__main__":
    # Importer pandas pour l'affichage des années
    import pandas as pd
    
    # Configurer le logging
    setup_logging(log_level="INFO")
    
    # Parser les arguments
    parser = argparse.ArgumentParser(
        description="Pipeline ATP Prediction"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Forcer le téléchargement des données"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Ne pas sauvegarder les fichiers intermédiaires"
    )
    
    args = parser.parse_args()
    
    # Exécuter le pipeline
    try:
        main(
            force_download=args.force_download,
            save_bronze=not args.no_save,
            save_silver=not args.no_save,
            save_gold=not args.no_save
        )
    except Exception as e:
        logger.exception(f"❌ Erreur fatale : {e}")
        raise