Projet 5 : Déploiement d'un Modèle de Machine Learning en Production

🚀 Mission : Rendre le Modèle Opérationnel

Ce projet s'inscrit dans le cadre d'une mission de freelance pour Futurisys, une entreprise souhaitant industrialiser ses modèles de Machine Learning. L'objectif principal est de transformer un modèle prédictif existant (que nous allons intégrer) en un service accessible et fiable via une API.

Livrables Clés :

API REST : Développée avec FastAPI pour exposer les prédictions du modèle.

Tests Unitaires : Mise en place de tests avec pytest pour garantir la fiabilité du code.

Gestion de Version : Utilisation de Git pour le suivi des modifications, avec un historique clair et l'utilisation de branches de fonctionnalités.

🏗 Architecture de la Solution

(Cette section sera complétée plus tard. Pour l'instant, elle sert de placeholder.)

Nous adopterons une architecture orientée service :

Modèle ML : Le modèle entraîné (à intégrer).

API Gateway : FastAPI gère les requêtes HTTP, la validation des données d'entrée (via Pydantic) et appelle le modèle.

Conteneurisation : (Ajouter Docker/Kubernetes si vous les utilisez dans les prochaines étapes).

🛠 Installation et Démarrage (Workflow uv)

Ce projet utilise le gestionnaire de paquets ultra-rapide uv pour la gestion des environnements virtuels et des dépendances, en se basant sur le fichier de configuration pyproject.toml.

Prérequis

Python 3.13.5 : La version de Python requise est gérée via pyenv pour assurer l'isolation (voir nos discussions).

uv : Assurez-vous d'avoir uv installé globalement (pip install uv).

1. Cloner le dépôt

git clone https://github.com/AgababyanArtur/OpenClassrooms_P5
cd Projet5


2. Configuration de l'environnement virtuel

Nous allons créer un environnement virtuel isolé et installer toutes les dépendances listées dans pyproject.toml.

# Créer l'environnement virtuel (.venv) en utilisant la version Python spécifiée par pyenv
uv venv

# Activer l'environnement
source .venv/bin/activate

# Installer les dépendances (y compris les dépendances de développement pour les tests, etc.)
uv pip install -e . --dev 


3. Lancer l'API

(À faire lors de l'étape 2. Vous devrez remplacer main.py par le nom de votre fichier principal FastAPI.)

# Lancement du serveur local Uvicorn
uvicorn main:app --reload


⚙ Utilisation de l'API

🤝 Contribution (Git Workflow)

Branche Principale : main ou master. Seules les versions stables et testées y sont mergées.

Branches de Fonctionnalités : Utiliser la convention feat/nom-de-la-feature (ex: feat/setup-fastapi).

Commits : Utiliser les Conventional Commits (feat:, fix:, docs:, etc.) pour un historique clair.

# Exemple de workflow pour une nouvelle fonctionnalité
git checkout main
git pull origin main
git checkout -b feat/ajout-api-prediction
# ... votre code ici ...
git commit -m "feat: Ajout de l'endpoint de prédiction /predict"
git push
