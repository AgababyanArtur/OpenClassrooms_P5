import pickle
from pathlib import Path

# Définition des chemins
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "model" / "modele_churn_light.pkl"

print(f"Chargement du modèle depuis : {MODEL_PATH}")

ml_model = None
churn_threshold = 0.235  # Valeur par défaut de sécurité
expected_features = []  # Liste des features attendues

if not MODEL_PATH.exists():
    print(f"❌ ERREUR : Le fichier {MODEL_PATH} est introuvable.")
else:
    try:
        # Chargement du package complet
        with open(MODEL_PATH, "rb") as file:
            model_package = pickle.load(file)

        # Extraction des métadonnées
        if isinstance(model_package, dict) and "model" in model_package:
            ml_model = model_package["model"]
            churn_threshold = model_package.get("threshold", 0.235)
            expected_features = model_package.get("features", [])

            print(f"✅ Modèle chargé. Seuil personnalisé : {churn_threshold}")
            print(f"✅ Nombre de features attendues : {len(expected_features)}")

            # Affichage des features pour debug
            if expected_features:
                print(f"✅ Features : {expected_features}")
        else:
            # Fallback : modèle brut sans métadonnées
            ml_model = model_package
            print("⚠️ Modèle chargé sans métadonnées (package non structuré)")

            # Tente de récupérer les features depuis sklearn
            if hasattr(ml_model, "feature_names_in_"):
                expected_features = list(ml_model.feature_names_in_)
                print(f"✅ Features récupérées depuis sklearn : {expected_features}")

    except Exception as e:
        print(f"❌ ERREUR : Impossible de charger le modèle : {e}")
        ml_model = None
