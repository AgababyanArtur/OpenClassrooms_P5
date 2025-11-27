import uvicorn
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ==========================================
# 1. Configuration et Chargement du Modèle
# ==========================================

app = FastAPI(
    title="API de Prédiction - Projet 5",
    description="API pour prédire le score/churn (adaptée aux 10 features du modèle).",
    version="1.0.0"
)

# ⚠️ Vérifie bien que ton fichier s'appelle exactement comme ça et est dans un dossier 'model'
MODEL_PATH = "model/mon_modele.joblib"

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle chargé avec succès depuis {MODEL_PATH}")
except Exception as e:
    print(f"❌ ERREUR CRITIQUE : Impossible de charger le modèle : {e}")
    # On ne stoppe pas l'app ici pour permettre le debug, mais le predict ne marchera pas
    model = None

# ==========================================
# 2. Définition du Schéma de Données
# ==========================================

class InputData(BaseModel):
    """
    Définit les données d'entrée. 
    Les types (float/int) doivent correspondre à ton X_test.
    """
    ratio_surcharge_anciennete: float
    nombre_participation_pee: int
    departement_consulting: float    # Correspond à 'departement_Consulting'
    age: int
    poste_consultant: float          # Correspond à 'poste_Consultant'
    tension_salaire: float
    statut_marital_marie: float      # Correspond à 'statut_marital_Marié(e)'
    annees_dans_l_entreprise: int
    satisfaction_globale_moyenne: float
    satisfaction_employee_nature_travail: int

# ==========================================
# 3. Définition des Endpoints
# ==========================================

@app.get("/")
def home():
    return {"message": "API fonctionnelle ! Va sur /docs pour tester la prédiction."}

@app.post("/predict")
def predict(data: InputData):
    if model is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé côté serveur.")

    try:
        # 1. Récupération des données envoyées par l'utilisateur
        input_data = data.model_dump()

        # 2. Création du DataFrame
        df = pd.DataFrame([input_data])

        # 3. 🚨 ÉTAPE CRUCIALE : RENOMMAGE DES COLONNES
        # Pydantic utilise des noms simples (minuscules, sans parenthèses),
        # mais ton modèle veut les noms EXACTS de l'entraînement.
        rename_dict = {
            "departement_consulting": "departement_Consulting",
            "poste_consultant": "poste_Consultant",
            "statut_marital_marie": "statut_marital_Marié(e)"
            # Les autres colonnes ont déjà le bon nom, donc pas besoin de les toucher
        }
        df = df.rename(columns=rename_dict)

        # 4. Vérification de l'ordre des colonnes (Optionnel mais recommandé)
        # Certains modèles (comme XGBoost sans feature names) sont sensibles à l'ordre.
        # On force l'ordre pour être sûr.
        expected_columns = [
            "ratio_surcharge_anciennete", "nombre_participation_pee", 
            "departement_Consulting", "age", "poste_Consultant", 
            "tension_salaire", "statut_marital_Marié(e)", 
            "annees_dans_l_entreprise", "satisfaction_globale_moyenne", 
            "satisfaction_employee_nature_travail"
        ]
        
        # On réorganise les colonnes pour matcher exactement X_test_subset
        df = df[expected_columns]

        # 5. Prédiction
        prediction = model.predict(df)
        
        # Gestion des probabilités (si le modèle le permet)
        probability = None
        if hasattr(model, "predict_proba"):
            # On prend souvent la probabilité de la classe 1 (positif/churn)
            probability = model.predict_proba(df)[0][1]

        # 6. Réponse
        return {
            "prediction": int(prediction[0]), # Convertit numpy.int64 en int Python standard
            "probability": probability
        }

    except Exception as e:
        # Affiche l'erreur dans la console serveur pour t'aider à débugger
        print(f"Erreur lors de la prédiction : {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# 4. Lancement
# ==========================================
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)