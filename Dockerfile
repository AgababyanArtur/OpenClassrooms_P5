FROM python:3.12-slim

WORKDIR /app

# 1. Installation des outils système (git et git-lfs sont requis !)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# 2. Récupération de uv (gestionnaire de paquets ultra-rapide)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Copie du projet
# Note : Sur Hugging Face Spaces, les fichiers LFS peuvent déjà être présents,
# mais COPY . . assure que tout le code (y compris main.py et le dossier app/) est bien là.
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

# --- MODIFICATION ICI ---
# On lance 'main:app' car le fichier s'appelle désormais main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
