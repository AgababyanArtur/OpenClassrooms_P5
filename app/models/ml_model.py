import pickle
from pathlib import Path

# Définition des chemins
# On remonte de : ml_model.py -> models/ -> app/ -> racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "model" / "model.pkl"

print(f"🔍 Recherche du modèle ici : {MODEL_PATH}")

ml_model = None

if not MODEL_PATH.exists():
    # 🛑 STOP : On arrête tout si le fichier n'est pas là.
    # Cela fera échouer le déploiement Hugging Face avec une erreur claire.
    raise FileNotFoundError(
        f"🚨 CRITIQUE : Le fichier modèle est introuvable : {MODEL_PATH}"
    )

try:
    with open(MODEL_PATH, "rb") as f:
        ml_model = pickle.load(f)
    print("✅ Modèle chargé avec succès !")
except Exception as e:
    raise RuntimeError(f"🚨 CRITIQUE : Impossible de lire le fichier pickle : {e}")
