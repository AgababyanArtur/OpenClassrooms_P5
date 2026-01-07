FROM python:3.13-slim

WORKDIR /app

# Outils système
RUN apt-get update && apt-get install -y \
    curl \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# UV et Dépendances
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY . .
RUN uv pip install --system . --no-cache

# --- LA TOUCHE MAGIQUE ---
# On lance le ré-entraînement ICI, dans l'environnement Docker final.
# Cela garantit que le modèle .joblib sera 100% compatible avec la version de scikit-learn installée.
RUN uv run python train_model.py

# Sécurité & Lancement
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user
ENV PATH="/home/user/.local/bin:$PATH"

EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
