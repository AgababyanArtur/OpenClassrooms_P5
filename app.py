import uvicorn
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ==========================================
# 1. Configuration et Chargement du Modèle
# ==========================================

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Prédiction Projet 5",
    description="Une API simple pour servir un modèle de Machine Learning.",
    version="1.0.0"
)

# Chargement du modèle au démarrage
# On le charge en variable globale pour ne pas le recharger à chaque requête
MODEL_PATH = "model/mon_modele.joblib" # Assure-toi que ce chemin est correct

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle chargé depuis {MODEL_PATH}")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle : {e}")
    model = None

# ==========================================
# 2. Définition du Schéma de Données (Pydantic)
# ==========================================

class InputData(BaseModel):
    """
    Définit la structure des données attendues par l'API.
    Les noms des variables doivent correspondre aux colonnes utilisées lors de l'entraînement.
    """
    # --- À MODIFIER CI-DESSOUS SELON TES FEATURES ---
    feature_1: float  # ex: age
    feature_2: float  # ex: revenu
    feature_3: int    # ex: nombre_enfants
    feature_4: str    # ex: categorie_socio_pro (si ton pipeline gère les strings)
    
    # Exemple concret (à effacer et remplacer par tes vraies données) :
    # sepal_length: float
    # sepal_width: float
    # petal_length: float
    # petal_width: float


# ==========================================
# 3. Définition des Endpoints
# ==========================================

@app.get("/")
def home():
    """Endpoint de base pour vérifier que l'API tourne."""
    return {"message": "Bienvenue sur l'API de prédiction ! Utilisez /docs pour tester."}

@app.post("/predict")
def predict(data: InputData):
    """
    Reçoit les données, les transforme en DataFrame et renvoie la prédiction.
    """
    # Vérification que le modèle est bien chargé
    if model is None:
        raise HTTPException(status_code=500, detail="Le modèle n'est pas disponible.")

    try:
        # 1. Conversion des données Pydantic en dictionnaire
        input_data = data.model_dump()

        # 2. Conversion en DataFrame pandas (format attendu par scikit-learn)
        # On met les données dans une liste ([input_data]) pour créer une seule ligne
        df = pd.DataFrame([input_data])

        # 3. Prédiction
        # Si c'est une classification, on peut vouloir la classe ET la probabilité
        prediction = model.predict(df)
        
        # Optionnel : Récupérer la probabilité (si le modèle le supporte)
        # probabilities = model.predict_proba(df).tolist() if hasattr(model, "predict_proba") else None

        # 4. Retour de la réponse en JSON
        # On utilise .tolist() ou .item() pour convertir les types numpy en types Python standard
        return {
            "prediction": prediction[0].item(), # La classe prédite (0 ou 1, ou nom de classe)
            # "probability": probabilities # Décommente si tu veux les probas
        }

    except Exception as e:
        # En cas d'erreur (ex: format de données incorrect pour le modèle)
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# 4. Lancement (Si exécuté directement)
# ==========================================
if __name__ == "__main__":
    # Permet de lancer le script via "python app.py"
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)