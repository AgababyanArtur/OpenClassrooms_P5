FROM python:3.13-slim

WORKDIR /app

# 1. Installation des outils système (git et git-lfs sont requis !)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# 2. Récupération de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Copie du projet
# Note : Sur Hugging Face Spaces, le contexte de build contient déjà les fichiers LFS téléchargés
# SI et SEULEMENT SI le repo a été cloné correctement.
# Mais pour être sûr, on copie tout.
COPY . .

# 4. Installation des dépendances
RUN uv pip install --system . --no-cache

# 5. Sécurité (Utilisateur non-root)
RUN useradd -m -u 1000 user
RUN chown -R user:user /app

USER user
ENV PATH="/home/user/.local/bin:$PATH"

# 6. Port et Lancement
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
