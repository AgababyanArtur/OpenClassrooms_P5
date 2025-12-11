FROM python:3.13-slim

WORKDIR /app

# Installation des outils système de base
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Récupération de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# --- OPTIMISATION DU CACHE ---
# On copie TOUT le projet (README, app.py, pyproject.toml...)
COPY . .

# On installe les dépendances
RUN uv pip install --system . --no-cache

# --- SÉCURITÉ & PERMISSIONS ---
# Création de l'utilisateur
RUN useradd -m -u 1000 user

# IMPORTANT : Donner les droits à l'utilisateur sur le dossier /app
# Sinon, s'il y a des fichiers temporaires ou des logs à écrire, ça plantera.
RUN chown -R user:user /app

USER user
ENV PATH="/home/user/.local/bin:$PATH"

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
