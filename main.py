import uvicorn
import pandas as pd
import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Imports de ta base de données (assure-toi que database.py est présent)
from database import SessionLocal, PredictionLog

# --- ARCHITECTURE MODULAIRE ---
# On importe le modèle déjà chargé depuis son module dédié
from app.models.ml_model import ml_model

# ==========================================
# 1. Configuration de l'API
# ==========================================

description = """
API de prédiction de churn (départ) des employés. 🚀

Cette API permet d'estimer la probabilité de départ d'un collaborateur
et enregistre chaque prédiction dans PostgreSQL pour la traçabilité.
"""

app = FastAPI(
    title="Projet 5 : API Churn Prediction",
    description=description,
    version="2.0.0",
)

# Dépendance pour la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. Schéma de Données (Pydantic)
# ==========================================

class InputData(BaseModel):
    """Schéma des caractéristiques employé attendues par le modèle."""
    ratio_surcharge_anciennete: float = Field(..., example=0.14)
    nombre_participation_pee: int = Field(..., example=0)
    departement_consulting: float = Field(..., example=0.0)
    age: int = Field(..., ge=18, le=100, example=41)
    poste_consultant: float = Field(..., example=0.0)
    tension_salaire: float = Field(..., example=0.0003)
    statut_marital_marie: float = Field(..., example=0.0)
    annees_dans_l_entreprise: int = Field(..., ge=0, example=2)
    satisfaction_globale_moyenne: float = Field(..., example=2.0)
    satisfaction_employee_nature_travail: int = Field(..., example=1)

    class Config:
        json_schema_extra = {
            "example": {
                "ratio_surcharge_anciennete": 0.14,
                "nombre_participation_pee": 0,
                "departement_consulting": 0.0,
                "age": 41,
                "poste_consultant": 0.0,
                "tension_salaire": 0.0003,
                "statut_marital_marie": 0.0,
                "annees_dans_l_entreprise": 2,
                "satisfaction_globale_moyenne": 2.0,
                "satisfaction_employee_nature_travail": 1,
            }
        }

# ==========================================
# 3. Routes de l'API
# ==========================================

@app.get("/")
def home():
    """Vérification de l'état de l'API."""
    return {"status": "online", "model_loaded": ml_model is not None}

@app.post("/predict", tags=["ML Prediction"])
def predict(input_data: InputData, db: Session = Depends(get_db)):
    """Effectue une prédiction et l'enregistre en BDD."""
    
    # Sécurité : Vérifier que le module a bien chargé le modèle
    if ml_model is None:
        raise HTTPException(
            status_code=500, detail="Erreur interne : Le modèle n'a pas pu être chargé."
        )

    try:
        # 1. Préparation des données pour Scikit-Learn
        data_dict = input_data.model_dump()
        df = pd.DataFrame([data_dict])

        # Mapping des colonnes (doit correspondre exactement au notebook d'entraînement)
        rename_mapping = {
            "statut_marital_marie": "statut_marital_Marié(e)",
            "departement_consulting": "departement_Consulting",
            "poste_consultant": "poste_Consultant",
        }
        df = df.rename(columns=rename_mapping)

        # Ordre strict des colonnes exigé par le modèle
        expected_columns = [
            "ratio_surcharge_anciennete", "nombre_participation_pee",
            "departement_Consulting", "age", "poste_Consultant",
            "tension_salaire", "statut_marital_Marié(e)",
            "annees_dans_l_entreprise", "satisfaction_globale_moyenne",
            "satisfaction_employee_nature_travail"
        ]
        df = df[expected_columns]

        # 2. Inférence (Prédiction)
        prediction_val = int(ml_model.predict(df)[0])
        proba_val = None
        if hasattr(ml_model, "predict_proba"):
            proba_val = float(ml_model.predict_proba(df)[0][1])

        # 3. 💾 Logging en Base de Données
        log_entry = PredictionLog(
            timestamp=datetime.datetime.now(),
            inputs=data_dict,
            prediction=prediction_val,
            probability=proba_val,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        return {
            "prediction": prediction_val,
            "probability": proba_val,
            "log_id": log_entry.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
