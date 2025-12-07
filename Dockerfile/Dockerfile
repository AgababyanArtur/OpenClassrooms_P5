# Utilisation de Python 3.13-slim pour être ISO avec ton pipeline CI/CD
FROM python:3.13-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Installation de curl et nettoyage du cache pour garder l'image légère
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Installation de uv (ton gestionnaire de paquets ultra-rapide)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 1. Copie de l'intégralité du projet
# Important : On copie tout AVANT d'installer pour que 'pip install .' trouve le projet
COPY . .

# 2. Installation des dépendances
# --system : installe directement dans le python global du conteneur
# --no-cache : gagne de l'espace disque
RUN uv pip install --system . --no-cache

# Création d'un utilisateur non-root pour la sécurité (Standard Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Exposition du port 7860
EXPOSE 7860

# Lancement de l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]