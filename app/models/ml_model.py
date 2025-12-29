import pickle
from pathlib import Path
import os

# Définition du chemin (attention à l'extension .pkl)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "model" / "mon_modele.pkl"

print(f"Chargement du modèle Pickle depuis : {MODEL_PATH}")

try:
    # --- CHANGEMENT ICI ---
    # On utilise le context manager 'with open' pour lire en mode binaire ('rb')
    with open(MODEL_PATH, "rb") as f:
        ml_model = pickle.load(f)
    print("✅ Modèle Pickle chargé avec succès.")
except Exception as e:
    print(f"❌ ERREUR : Impossible de charger le modèle Pickle : {e}")
    ml_model = None
    