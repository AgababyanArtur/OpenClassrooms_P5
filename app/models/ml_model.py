import pickle
from pathlib import Path
import os

# Définition des chemins
# On remonte de : ml_model.py -> models/ -> app/ -> racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "model" / "mon_modele.pkl"

print(f"Chargement du modèle depuis : {MODEL_PATH}")

ml_model = None

if not MODEL_PATH.exists():
    print(f"❌ ERREUR : Le fichier {MODEL_PATH} est introuvable.")
else:
    try:
        # --- LA CORRECTION EST ICI ---
        # On doit ouvrir le fichier avec open(..., "rb")
        with open(MODEL_PATH, "rb") as f:
            ml_model = pickle.load(f)
        print("✅ Modèle Pickle chargé avec succès dans le module app.models.ml_model")
    except Exception as e:
        print(f"❌ ERREUR : Impossible de charger le modèle : {e}")
