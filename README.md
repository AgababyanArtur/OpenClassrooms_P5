:README.md
---
title: Projet 5 Churn Prediction
emoji: 🔮
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🔮 Projet 5 : API de Prédiction de Churn Employé

## 📄 Description

Ce projet est une solution MLOps complète visant à prédire le risque de départ (Churn) d'un employé au sein d'une entreprise.
Il permet aux équipes RH d'anticiper les départs grâce à une API REST exposant un modèle de Machine Learning entraîné sur des données historiques.

[👉 Voir la Fiche Technique du Modèle (Model Card)] (https://github.com/AgababyanArtur/OpenClassrooms_P5/blob/main/MODEL_CARD.md) pour les détails sur les performances et les biais.

L'architecture respecte les principes DevOps/MLOps :

* API : FastAPI (rapide et typé).

* Database : PostgreSQL pour l'historisation des prédictions (Traçabilité).

* Qualité : Tests unitaires (pytest), Linting (Ruff), Formatage (Black).

* CI/CD : Pipeline GitHub Actions automatisé.

* Déploiement : Conteneurisation Docker sur Hugging Face Spaces.

## 🏗️ Architecture Technique

Le projet est structuré comme suit :

* app.py : Point d'entrée de l'API FastAPI.

* model/ : Contient le modèle entraîné (.joblib).

* tests/ : Suite de tests unitaires et fonctionnels.

* database.py : Gestion de la connexion BDD (SQLAlchemy).

* create_tables.py / init_db.py : Scripts d'initialisation de la base de données.

* .github/workflows/ : Pipeline CI/CD.

## 📊 Gestion des Données & Monitoring

Pour assurer la fiabilité du modèle dans le temps, une architecture de données rigoureuse a été mise en place :

1. **Stockage :** Toutes les interactions avec l'API (entrées utilisateurs + prédiction du modèle + probabilités) sont enregistrées systématiquement dans la table prediction_logs d'une base PostgreSQL.

2. **Traçabilité :** Chaque réponse API contient un log_id unique permettant de retrouver les conditions exactes de la prédiction.

3. **Analytique (Futur) :** Ces logs sont structurés pour alimenter un futur tableau de bord (Dashboard) permettant de surveiller :

    * Le taux de churn prédit moyen sur la période.

    * La dérive des données (Data Drift) en comparant les inputs récents avec le dataset d'entraînement.

## 🚀 Installation et Démarrage

**Prérequis**

    * Python 3.12 ou supérieur

    * Docker (optionnel)

    * Git

**1. Clonage du projet**
    ```bash
    git clone [https://github.com/AgababyanArtur/OpenClassrooms_P5.git](https://github.com/AgababyanArtur/OpenClassrooms_P5.git)
    cd OpenClassrooms_P5
    ```

**2. Installation (Local)**

    Nous recommandons l'utilisation de uv pour la rapidité, ou pip.
    ```bash
    # Avec pip
    pip install .

    # Avec uv (recommandé)
    uv pip install --system .
    ```

**3. Configuration**

    Créez un fichier .env à la racine pour configurer la base de données :
    ```bash
    DATABASE_URL=postgresql://user:password@localhost/dbname
    ```

    *Note : Pour les tests unitaires, une base SQLite en mémoire est utilisée automatiquement, aucune configuration n'est requise.*

**4. Lancement de l'API**
    ```bash
    uvicorn app:app --reload
    ```

L'API sera accessible sur ```url http://127.0.0.1:8000```.

## 🐳 Utilisation avec Docker

Pour lancer l'application dans un conteneur isolé (environnement iso-prod) :
```bash
# 1. Construire l'image
docker build -t churn-api .

# 2. Lancer le conteneur (Port 7860 pour compatibilité Hugging Face)
docker run -p 7860:7860 churn-api
```

Accès : ```url http://localhost:7860```

## 🧪 Tests et Qualité

La robustesse du code est assurée par une suite de tests automatisés couvrant les cas nominaux, les erreurs (405, 500) et la validation des données (422).
```bash
# Lancer les tests
uv run pytest tests/

# Vérifier la couverture de code
uv run pytest --cov=app tests/
```

## 📚 Documentation API

La documentation interactive (Swagger UI) est générée automatiquement par FastAPI.

Une fois l'API lancée, visitez :

* Swagger : ```url http://127.0.0.1:8000/docs``` 

* Redoc : ```url http://127.0.0.1:8000/redoc```

Endpoint Principal : /predict

* Méthode : POST

* Input : JSON contenant les caractéristiques de l'employé (age, ancienneté, etc.).

* Output : Prédiction (0 ou 1), probabilité associée et ID de traçabilité.

# 👤 Auteur

Artur Agababyan - Étudiant Data Scientist OpenClassrooms.