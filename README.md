---
title: Mon Projet 5 Data Science
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

## Projet 5 : Déploiement d'un Modèle de Machine Learning en Production

🚀 Mission : Rendre le Modèle Opérationnel

Ce projet répond à une demande de l'entreprise Futurisys. L'objectif est d'industrialiser un modèle de Machine Learning permettant de prédire le churn (départ des employés).

Nous passons d'une analyse exploratoire (Notebook) à une véritable application en production (API), capable de recevoir des données, faire une prédiction et stocker l'historique pour le suivi (MLOps).

🏗 Architecture Technique

1. L'application repose sur une architecture 3-tiers :
2. L'API (FastAPI - app.py) : C'est le point d'entrée. Elle reçoit les requêtes HTTP, valide les données avec Pydantic et interroge le modèle.
3. Le Modèle (Machine Learning - model/mon_modele.joblib) : Un modèle entraîné (Scikit-Learn/XGBoost) qui effectue la classification binaire (0: Reste, 1: Part).
    * La Base de Données (PostgreSQL - database.py) :
    * Stocke l'historique des employés (employees_history).
    * Trace toutes les prédictions réalisées par l'API (prediction_logs) pour surveiller la performance dans le temps.

🛠 Installation et Configuration

Ce projet utilise uv pour une gestion ultra-rapide des dépendances.

1. Prérequis

    * Un système Linux/Mac ou WSL (Windows).
    * Python 3.12+ installé.
    * PostgreSQL installé et un serveur local en cours d'exécution.
    * L'outil uv installé (pip install uv).

2. Cloner le projet
    git clone [https://github.com/AgababyanArtur/OpenClassrooms_P5.git](https://github.com/AgababyanArtur/OpenClassrooms_P5.git)
    cd Projet5

3. Configuration de l'environnement (.env)
    Pour des raisons de sécurité, les identifiants ne sont pas dans le code.
    Créez un fichier .env à la racine du projet :

    touch .env


    Ouvrez-le et ajoutez votre configuration PostgreSQL :

    # .env
    DATABASE_URL=postgresql://postgres:votre_mot_de_passe@localhost/projet5_db


4. Installation des dépendances

    # Créer l'environnement virtuel
    uv venv

    # Activer l'environnement
    source .venv/bin/activate

    # Installer toutes les dépendances (y compris de dev)
    uv pip install -e . --dev


5. Initialisation de la Base de Données

    Ce script va créer les tables et importer les données historiques depuis le CSV.

    python init_db.py


🚀 Démarrage de l'API

Une fois installé, lancez le serveur de développement :

uvicorn app:app --reload

app : correspond au fichier app.py.

app (le deuxième) : correspond à l'objet app = FastAPI(...) dans le fichier.

--reload : redémarre le serveur si vous modifiez le code.

L'API est accessible sur : http://127.0.0.1:8000

⚙ Utilisation de l'API

1. Documentation interactive (Swagger UI)

Rendez-vous sur http://127.0.0.1:8000/docs.
Vous pourrez tester l'endpoint /predict directement depuis votre navigateur sans écrire de code.

2. Exemple de requête (cURL)

curl -X 'POST' \
  '[http://127.0.0.1:8000/predict](http://127.0.0.1:8000/predict)' \
  -H 'Content-Type: application/json' \
  -d '{
    "ratio_surcharge_anciennete": 0.15,
    "nombre_participation_pee": 2,
    "departement_consulting": 1.0,
    "age": 34,
    "poste_consultant": 1.0,
    "tension_salaire": 0.005,
    "statut_marital_marie": 1.0,
    "annees_dans_l_entreprise": 5,
    "satisfaction_globale_moyenne": 3.5,
    "satisfaction_employee_nature_travail": 1
  }'


Réponse attendue :

{
  "prediction": 0,
  "probability": 0.12,
  "log_id": 42
}


✅ Tests Unitaires

La qualité du code est assurée par pytest. Les tests utilisent une base de données SQLite en mémoire pour ne pas impacter votre base PostgreSQL de production.

Pour lancer la suite de tests :

pytest


Si tout est vert, le projet est stable !

🤝 Auteur

Projet réalisé par Artur Agababyan dans le cadre de la formation Data Scientist OpenClassrooms.