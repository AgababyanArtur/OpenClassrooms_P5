# ==========================================
# ÉTAPE 1 : Image de base Python 3.13
# ==========================================
FROM docker.io/library/python:3.13-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système (Git LFS, curl)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# ==========================================
# ÉTAPE 2 : Installer UV
# ==========================================
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# ==========================================
# ÉTAPE 3 : Copier le projet
# ==========================================
COPY . .

# ==========================================
# ÉTAPE 4 : Installer les dépendances Python
# ==========================================
RUN uv pip install --system . --no-cache

# ==========================================
# ÉTAPE 5 : Créer un utilisateur non-root
# ==========================================
RUN useradd -m -u 1000 user
RUN chown -R user:user /app

# Passer à l'utilisateur non-root
USER user

# ==========================================
# ÉTAPE 6 : Exposer le port
# ==========================================
EXPOSE 7860

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./churn.db

# ==========================================
# ÉTAPE 7 : Commande de démarrage
# ==========================================
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
