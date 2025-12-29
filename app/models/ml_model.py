import pickle
from pathlib import Path
import os

# Définition des chemins
# On remonte de : ml_model.py -> models/ -> app/ -> racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "model" / "mon_modele.pkl"

print(f"Chargement du modèle depuis : {MODEL_PATH}")

try:
    # On charge le modèle dans la variable 'ml_model' qui sera exportée
    ml_model = pickle.load(MODEL_PATH)
    print("✅ Modèle chargé avec succès dans le module app.models.ml_model")
except Exception as e:
    print(f"❌ ERREUR : Impossible de charger le modèle : {e}")
    ml_model = None
