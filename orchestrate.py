#!/usr/bin/env python
"""
Orchestrateur simple pour le pipeline ATP.

Workflow:
1. run_pipeline.py → Collecte et préparation des données
2. train_model.py  → Entraînement et sauvegarde model_YYYYMMDD.pkl

Usage:
    python orchestrate.py
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def log(message: str, level: str = "INFO"):
    """Affiche un message avec timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icon = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} {message}")


def run_script(script: str, description: str, timeout: int = 3600) -> bool:
    """
    Exécute un script Python.
    
    Args:
        script: Nom du script ou module Python
        description: Description de l'étape
        timeout: Timeout en secondes
    
    Returns:
        True si succès, False sinon
    """
    log(f"{description}...", "INFO")
    
    try:
        python = sys.executable
        
        # Module Python (src.ml.train_model) ou script direct (run_pipeline.py)
        if script.startswith("src."):
            cmd = [python, "-m", script]
        else:
            cmd = [python, script]
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        log(f"{description} - Succès", "SUCCESS")
        return True
        
    except subprocess.TimeoutExpired:
        log(f"{description} - Timeout ({timeout}s)", "ERROR")
        return False
        
    except subprocess.CalledProcessError as e:
        log(f"{description} - Échec (code {e.returncode})", "ERROR")
        if e.stderr:
            print(e.stderr[:500])
        return False
    
    except Exception as e:
        log(f"{description} - Erreur: {e}", "ERROR")
        return False


def main():
    """Orchestration principale."""
    start_time = datetime.now()
    
    print("=" * 70)
    log("DÉMARRAGE ORCHESTRATION ATP", "INFO")
    print("=" * 70)
    
    # Étape 1: Pipeline de données
    if not run_script("run_pipeline.py", "Étape 1/2 : Pipeline de données", timeout=7200):
        log("Pipeline échoué, arrêt", "ERROR")
        return 1
    
    # Étape 2: Entraînement du modèle
    if not run_script("src.ml.train_model", "Étape 2/2 : Entraînement du modèle", timeout=1800):
        log("Entraînement échoué, arrêt", "ERROR")
        return 1
    
    # Résumé
    duration = (datetime.now() - start_time).total_seconds()
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    
    print("=" * 70)
    log(f"ORCHESTRATION TERMINÉE - Durée: {minutes}m {seconds}s", "SUCCESS")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())