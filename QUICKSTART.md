# 🚀 Guide de Démarrage Rapide

## Installation (5 minutes)

### 1. Cloner le repo
```bash
git clone https://github.com/adechielie/ATP-Prediction.git
cd ATP-Prediction
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

---

## Premier lancement (10 minutes)

### 1. Exécuter le pipeline de données
```bash
# Télécharge et prépare toutes les données
python run_pipeline.py

# Avec options :
python run_pipeline.py --force-download  # Force le téléchargement
python run_pipeline.py --no-save          # Ne sauvegarde pas les fichiers intermédiaires
```

**Sortie attendue :**
```
🚀 ATP PREDICTION - PIPELINE DÉMARRÉ
📥 ÉTAPE 1/4 : Collecte des données ATP...
✅ Données ATP chargées : 67,919 matchs
🌤️  Collecte des données climatiques...
✅ Données climatiques chargées : 1,099,625 enregistrements
🧹 ÉTAPE 2/4 : Preprocessing des données...
✅ Données nettoyées : 45,123 matchs
⚙️  ÉTAPE 3/4 : Feature engineering...
✅ Features créées : 85 colonnes
✅ PIPELINE TERMINÉ AVEC SUCCÈS
```

**Temps d'exécution :** ~8-10 minutes (première fois)

### 2. Lancer l'application Streamlit
```bash
streamlit run app_streamlit.py
```

L'application s'ouvre automatiquement dans votre navigateur à `http://localhost:8501`

---

## Utilisation sur VS Code

### 1. Ouvrir le projet
```bash
code .
```

### 2. Sélectionner l'interpréteur Python
1. `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (Mac)
2. Taper "Python: Select Interpreter"
3. Choisir `./venv/bin/python`

### 3. Extensions recommandées
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Black Formatter** (Microsoft)
- **GitLens** (Eric Amodio)
- **Better Comments** (Aaron Bond)

### 4. Configuration VS Code

Créer `.vscode/settings.json` :
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

---

## Workflow Git

### 1. Initialiser Git (si nouveau repo)
```bash
git init
git add .
git commit -m "Initial commit: ATP Prediction refactored"
```

### 2. Connecter à GitHub
```bash
# Remplacer par votre URL GitHub
git remote add origin https://github.com/adechielie/ATP-Prediction.git
git branch -M main
git push -u origin main
```

### 3. Workflow quotidien
```bash
# 1. Créer une branche pour nouvelle feature
git checkout -b feature/nouvelle-feature

# 2. Faire vos modifications
# ...

# 3. Commit
git add .
git commit -m "Add: description de la feature"

# 4. Push vers GitHub
git push origin feature/nouvelle-feature

# 5. Créer une Pull Request sur GitHub
# 6. Merger après review

# 7. Revenir sur main et pull
git checkout main
git pull origin main
```

---

## Commandes utiles

### Pipeline de données
```bash
# Pipeline complet
python run_pipeline.py

# Forcer re-téléchargement
python run_pipeline.py --force-download

# Sans sauvegardes intermédiaires (plus rapide)
python run_pipeline.py --no-save
```

### Streamlit
```bash
# Lancer l'app
streamlit run app_streamlit.py

# Sur un port spécifique
streamlit run app_streamlit.py --server.port 8502

# Mode debug
streamlit run app_streamlit.py --server.runOnSave true
```

### Tests
```bash
# Tous les tests
pytest tests/

# Tests avec couverture
pytest --cov=src tests/

# Tests spécifiques
pytest tests/test_preprocessor.py -v
```

### Code quality
```bash
# Formatter le code
black src/

# Linter
flake8 src/

# Type checking
mypy src/
```

---

## Structure des fichiers créés

Après `run_pipeline.py` :

```
data/
├── raw/
│   ├── atp_matches_2000.csv
│   ├── atp_matches_2001.csv
│   ├── ...
│   └── climate_data.csv
│
├── bronze/
│   ├── atp_matches_bronze.csv      # Données brutes consolidées
│   └── climate_bronze.csv
│
├── silver/
│   └── atp_matches_silver.csv      # Données nettoyées
│
└── gold/
    └── atp_matches_gold.csv        # Features ML prêtes
```

---

## Problèmes courants

### Erreur : Module not found
```bash
# Solution : Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur : No local data found
```bash
# Solution : Télécharger les données
python run_pipeline.py --force-download
```

### Streamlit ne démarre pas
```bash
# Solution : Vérifier l'installation
pip install streamlit --upgrade
streamlit --version
```

### Git push rejected
```bash
# Solution : Pull d'abord
git pull origin main
# Résoudre les conflits si nécessaire
git push origin main
```

---

## Déploiement sur todoba.net

### Option 1 : Streamlit Cloud (Gratuit)
1. Pusher sur GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Connecter le repo
4. Déployer

### Option 2 : Serveur VPS
```bash
# Sur le serveur
git clone https://github.com/adechielie/ATP-Prediction.git
cd ATP-Prediction
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py

# Lancer avec nohup
nohup streamlit run app_streamlit.py --server.port 8501 &

# Avec reverse proxy Nginx
# Configurer /etc/nginx/sites-available/todoba.net
```

### Option 3 : Docker
```bash
# Construire l'image
docker build -t atp-prediction .

# Lancer le container
docker run -p 8501:8501 atp-prediction
```

---

## Support

**Questions ?** Créer une issue sur GitHub :
https://github.com/adechielie/ATP-Prediction/issues

**Bugs ?** Créer une issue avec :
- Description du problème
- Étapes pour reproduire
- Logs d'erreur
- Version Python / OS
