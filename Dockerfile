FROM python:3.13-slim

WORKDIR /app

# Installation des outils système
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Récupération de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# --- CHANGEMENT ICI ---
# On copie TOUT le projet (README, app.py, pyproject.toml...) D'ABORD
COPY . .

# Ensuite, on installe les dépendances et le projet
# Maintenant, l'installateur trouvera bien le README.md !
RUN uv pip install --system . --no-cache

# --- SÉCURITÉ ---
RUN useradd -m -u 1000 user
RUN chown -R user:user /app

USER user
ENV PATH="/home/user/.local/bin:$PATH"

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]