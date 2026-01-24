---
title: Projet 5 Churn Prediction
emoji: 🔮
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🔮 API de Prédiction du Churn (Employee Attrition)

Ce projet est une API REST développée avec **FastAPI** qui expose un modèle de Machine Learning (**Random Forest**) capable de prédire le risque de départ d'un employé (*Churn*).

L'objectif est de fournir aux équipes RH un outil d'aide à la décision pour anticiper les départs et améliorer la rétention des talents.

## 📑 Sommaire

- [Fonctionnalités](#-fonctionnalités)
- [Architecture & Stack Technique](#-architecture--stack-technique)
- [Modèle de Données (BDD)](#-modèle-de-données-bdd)
- [Installation & Démarrage Local](#-installation--démarrage-local)
- [Utilisation de l'API](#-utilisation-de-lapi)
- [Tests & Qualité](#-tests--qualité)
- [Déploiement (CI/CD)](#-déploiement-cicd)

## 🚀 Fonctionnalités

* **Prédiction en temps réel** : Estimation du risque de départ (0 ou 1) à partir de données socio-professionnelles.
* **Monitoring & Traçabilité** : Chaque requête est enregistrée dans une base de données PostgreSQL pour le suivi de la performance (*Data Drift*).
* **Documentation interactive** : Swagger UI intégré.
* **Robustesse** : Validation stricte des données d'entrée avec **Pydantic V2**.

## 🏗 Architecture & Stack Technique

Le projet suit une architecture modulaire :

* **Langage** : Python 3.12
* **API Framework** : FastAPI + Uvicorn
* **ML Engine** : Scikit-Learn (RandomForestClassifier)
* **Base de Données** : PostgreSQL (via SQLAlchemy)
* **Gestionnaire de paquets** : `uv` (remplaçant moderne de pip/poetry)
* **Conteneurisation** : Docker

## 💾 Modèle de Données (BDD)

Afin d'assurer le monitoring du modèle en production, toutes les prédictions sont historisées dans la table `prediction_logs`.

### Schéma de la table `prediction_logs`

Cette table permet de comparer *a posteriori* les prédictions faites par le modèle avec la réalité (*Ground Truth*), afin de calculer les métriques de performance dans le temps.

| Colonne | Type (SQL) | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Clé primaire auto-incrémentée. |
| `timestamp` | DATETIME | Date et heure de la prédiction. |
| `ratio_surcharge...` | FLOAT | Feature : Charge de travail / Ancienneté. |
| `age` | INTEGER | Feature : Âge de l'employé. |
| ... | ... | (Autres features d'entrée stockées individuellement) |
| `prediction` | INTEGER | Résultat du modèle : 0 (Reste) ou 1 (Départ). |
| `probability` | FLOAT | Score de confiance du modèle (ex: 0.76). |

> **Note** : La base de données est initialisée automatiquement au démarrage via le script `init_db.py`.

## ⚙️ Installation & Démarrage Local

Ce projet utilise `uv`, un gestionnaire de paquets ultra-rapide écrit en Rust.

### Prérequis

* Python 3.12+
* Git

### 1. Cloner le projet

```bash
git clone [https://github.com/agababyanartur/openclassrooms_p5.git](https://github.com/agababyanartur/openclassrooms_p5.git)
cd openclassrooms_p5
```

### 2. Environnement Virtuel & Dépendances

L'installation et la synchronisation des dépendances se font en une seule commande grâce à `uv`.
```bash
# Installe uv (si ce n'est pas déjà fait)
pip install uv

# Installe les dépendances et crée l'environnement virtuel (.venv)
uv sync
```

### 3. Configuration

Créez un fichier `.env` à la racine (optionnel si vous utilisez les valeurs par défaut pour le développement) :

```bash
DATABASE_URL=sqlite:///./churn.db  # Pour test local rapide
# OU pour PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 4. Lancer l'API

Utilisez `uv run` pour exécuter la commande dans l'environnement virtuel sans avoir besoin de l'activer manuellement.
```bash
uv run uvicorn main:app --reload
```

L'API sera accessible sur : `http://127.0.0.1:8000`

## 🔌 Utilisation de l'API

**Accès à la documentation (Swagger)**

Une fois l'API lancée, rendez-vous sur : 👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Exemple de requête (cURL)**
```bash
curl -X 'POST' \
  '[http://127.0.0.1:8000/predict](http://127.0.0.1:8000/predict)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ratio_surcharge_anciennete": 0.14,
  "nombre_participation_pee": 0,
  "statut_marital_divorce": 0.0,
  "age": 41,
  "annees_dans_l_entreprise": 2,
  "frequence_deplacement_frequent": 1.0,
  "poste_representant_commercial": 0.0,
  "niveau_education": 3,
  "domaine_etude_marketing": 0.0,
  "poste_consultant": 1.0
}'
```

**Réponse attendue :**
```json
{
  "prediction": 0,
  "probability": 0.12,
  "threshold_used": 0.235,
  "log_id": 1
}
```

## ✅ Tests & Qualité

Les tests unitaires et d'intégration sont gérés par **Pytest**. Pour lancer la suite de tests via `uv` :
```bash
uv run pytest
```

## 🚢 Déploiement (CI/CD)

Le projet inclut un pipeline d'intégration continue via GitHub Actions (fichier `.github/workflows/ci_pipeline.yml`).

À chaque push sur la branche `main` :

1. Installation de uv et des dépendances.

2. Exécution des tests automatisés (uv run pytest).

3. (Optionnel) Build de l'image Docker.

Pour lancer avec Docker manuellement :
```bash
docker build -t churn-api .
docker run -p 8000:8000 churn-api
```
Projet réalisé dans le cadre de la formation Data Scientist Machine Learning OpenClassrooms - Projet 5.