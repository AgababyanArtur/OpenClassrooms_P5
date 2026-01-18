FROM python:3.12-slim

WORKDIR /app

# 1. Installation des outils système
# git et git-lfs sont utiles si jamais on doit récupérer des fichiers, 
# mais ici on génère le modèle sur place.
RUN apt-get update && apt-get install -y \
    curl \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# 2. Récupération de uv (gestionnaire de paquets)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Copie de l'intégralité du projet
# Cela inclut 'train_model.py' et 'final_data_set.csv' qui sont indispensables
COPY . .

# 4. Installation des dépendances Python
# --system : installe dans l'environnement global du conteneur
RUN uv pip install --system . --no-cache

# 5. 🏗️ ÉTAPE CRITIQUE : RÉ-ENTRAÎNEMENT DU MODÈLE
# On s'assure que le dossier de sortie existe
RUN mkdir -p model

# On lance le script
RUN uv run python train_model.py

# 6. Sécurité & Permissions
# On crée un utilisateur non-root pour l'exécution
RUN useradd -m -u 1000 user
# On donne la propriété du dossier /app à cet utilisateur (pour qu'il puisse lire le modèle généré)
RUN chown -R user:user /app

USER user
ENV PATH="/home/user/.local/bin:$PATH"

# 7. Lancement de l'API
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]