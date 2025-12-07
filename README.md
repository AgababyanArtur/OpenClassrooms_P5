---
title: Mon Projet 5 Data Science
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

Projet 5 : Déploiement d'un modèle de prédiction de Churn

Ce projet vise à industrialiser un modèle de Machine Learning permettant de prédire le risque de départ (Churn) d'un employé.
L'application expose le modèle via une API FastAPI, stocke les historiques de prédiction dans une base PostgreSQL, et est déployée automatiquement sur Hugging Face Spaces via un pipeline CI/CD.

🚀 Fonctionnalités

API REST rapide et documentée (FastAPI).

Modèle ML : Prédiction binaire (Churn / Pas Churn) avec probabilités.

Validation des données robuste avec Pydantic.

Traçabilité : Chaque requête est loggée en base de données.

CI/CD : Tests et déploiement automatisés via GitHub Actions.

Conteneurisation : Application packagée avec Docker.

🛠️ Installation en local

Prérequis

Python 3.12+

PostgreSQL (ou adaptation pour SQLite)

uv (recommandé) ou pip

1. Cloner le projet

git clone [https://github.com/TonPseudo/TonProjet.git](https://github.com/TonPseudo/TonProjet.git)
cd TonProjet


2. Installer les dépendances

Avec uv (plus rapide) :

uv pip install -r pyproject.toml --system


Ou avec pip classique :

pip install .


3. Configurer la Base de Données

Assurez-vous d'avoir une base PostgreSQL active. Modifiez l'URL de connexion dans database.py si nécessaire, ou définissez une variable d'environnement (recommandé pour la prod).

# Créer les tables
python create_tables.py

# (Optionnel) Peupler avec des données initiales
python init_db.py


4. Lancer l'API

uvicorn app:app --reload


L'API sera accessible sur : http://127.0.0.1:8000

🧪 Tests et Qualité

Le projet inclut une suite de tests unitaires (pytest) et une analyse de qualité de code (Ruff, Black).

Pour lancer les tests avec couverture de code :

uv run pytest --cov=app tests/


Pour vérifier le formatage :

uv run ruff check .
uv run black --check .


🐳 Utilisation avec Docker

L'application est prête à être conteneurisée.

Construire l'image

docker build -t projet5-churn-api .


Lancer le conteneur

docker run -p 7860:7860 projet5-churn-api


L'API sera accessible sur http://localhost:7860.

📚 Documentation API (Swagger)

Une fois l'application lancée, la documentation interactive est disponible sur :

Swagger UI : /docs (Testez les endpoints en direct)

ReDoc : /redoc

Endpoint Principal : /predict

Méthode : POST

Description : Reçoit les données d'un employé et retourne la prédiction de churn.

Exemple de Body :

{
  "ratio_surcharge_anciennete": 0.14,
  "nombre_participation_pee": 0,
  "departement_consulting": 0.0,
  "age": 41,
  "poste_consultant": 0.0,
  "tension_salaire": 0.0003,
  "statut_marital_marie": 0.0,
  "annees_dans_l_entreprise": 2,
  "satisfaction_globale_moyenne": 2.0,
  "satisfaction_employee_nature_travail": 1
}


⚙️ Pipeline CI/CD

Le projet utilise GitHub Actions pour l'intégration continue.

Job build-and-test : Installe les dépendances, vérifie le code (Lint) et lance les tests.

Job deploy-to-huggingface : Si les tests passent (sur la branche main), le code est déployé automatiquement sur Hugging Face Spaces.

👤 Auteur

Artur Agababyan - Étudiant Data Scientist