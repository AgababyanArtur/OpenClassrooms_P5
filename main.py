import uvicorn
import pandas as pd
import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from database import SessionLocal, PredictionLog, Base, engine

try:
    from app.models.ml_model import ml_model, churn_threshold
except ImportError:
    from app.models.ml_model import ml_model

    churn_threshold = 0.5

# ==========================================
# 0. Lifespan Event (Création auto des tables)
# ==========================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Événement exécuté au démarrage et à l'arrêt de l'API."""
    print("🚀 Démarrage de l'API...")

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables de la base de données vérifiées/créées avec succès !")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création des tables : {e}")

    yield

    print("🛑 Arrêt de l'API...")


# ==========================================
# 1. Configuration de l'API
# ==========================================

description = """
API de prédiction de churn (départ) des employés. 🚀
"""

app = FastAPI(
    title="Projet 5 : API Churn Prediction",
    description=description,
    version="2.3.0",
    lifespan=lifespan,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 2. Schéma de Données
# ==========================================


class InputData(BaseModel):
    """Schéma des 10 caractéristiques correspondant EXACTEMENT au modèle."""

    ratio_surcharge_anciennete: float = Field(..., json_schema_extra={"example": 0.14})
    nombre_participation_pee: int = Field(..., json_schema_extra={"example": 0})
    statut_marital_divorce: float = Field(
        ...,
        json_schema_extra={"example": 0.0},
        description="1.0 si divorcé(e), 0.0 sinon",
    )
    age: int = Field(..., ge=18, le=100, json_schema_extra={"example": 41})
    annees_dans_l_entreprise: int = Field(..., ge=0, json_schema_extra={"example": 2})
    frequence_deplacement_frequent: float = Field(
        ...,
        json_schema_extra={"example": 0.0},
        description="1.0 si déplacements fréquents, 0.0 sinon",
    )
    poste_representant_commercial: float = Field(
        ...,
        json_schema_extra={"example": 0.0},
        description="1.0 si Représentant Commercial, 0.0 sinon",
    )
    niveau_education: int = Field(
        ..., ge=1, le=5, json_schema_extra={"example": 3}, description="Niveau 1-5"
    )
    domaine_etude_marketing: float = Field(
        ...,
        json_schema_extra={"example": 0.0},
        description="1.0 si Marketing, 0.0 sinon",
    )
    poste_consultant: float = Field(
        ...,
        json_schema_extra={"example": 1.0},
        description="1.0 si Consultant, 0.0 sinon",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ratio_surcharge_anciennete": 0.14,
                "nombre_participation_pee": 0,
                "statut_marital_divorce": 0.0,
                "age": 41,
                "annees_dans_l_entreprise": 2,
                "frequence_deplacement_frequent": 1.0,
                "poste_representant_commercial": 0.0,
                "niveau_education": 3,
                "domaine_etude_marketing": 0.0,
                "poste_consultant": 1.0,
            }
        }
    )


# ==========================================
# 3. Routes de l'API
# ==========================================


@app.get("/")
def home():
    """Vérification de l'état de l'API."""
    return {
        "status": "online",
        "model_loaded": ml_model is not None,
        "threshold_configured": churn_threshold,
        "message": "API connectée à PostgreSQL !",
        "model_version": "light (10 features)",
    }


@app.post("/predict", tags=["ML Prediction"])
def predict(input_data: InputData, db: Session = Depends(get_db)):
    """Effectue une prédiction et l'enregistre en BDD."""

    if ml_model is None:
        raise HTTPException(
            status_code=500, detail="Erreur interne : Le modèle n'a pas pu être chargé."
        )

    try:
        # 1. Préparation des données
        data_dict = input_data.model_dump()
        df = pd.DataFrame([data_dict])

        # 2. Mapping vers les noms EXACTS du modèle
        rename_mapping = {
            "statut_marital_divorce": "statut_marital_Divorcé(e)",
            "frequence_deplacement_frequent": "frequence_deplacement_Frequent",
            "poste_representant_commercial": "poste_Représentant Commercial",
            "domaine_etude_marketing": "domaine_etude_Marketing",
            "poste_consultant": "poste_Consultant",
        }
        df = df.rename(columns=rename_mapping)

        # 3. ORDRE EXACT des colonnes
        expected_columns = [
            "ratio_surcharge_anciennete",
            "nombre_participation_pee",
            "statut_marital_Divorcé(e)",
            "age",
            "annees_dans_l_entreprise",
            "frequence_deplacement_Frequent",
            "poste_Représentant Commercial",
            "niveau_education",
            "domaine_etude_Marketing",
            "poste_Consultant",
        ]

        df = df[expected_columns]

        # 4. Inférence
        proba_val = None
        prediction_val = 0

        if hasattr(ml_model, "predict_proba"):
            proba_val = float(ml_model.predict_proba(df)[0][1])
            prediction_val = 1 if proba_val >= churn_threshold else 0
        else:
            prediction_val = int(ml_model.predict(df)[0])
            proba_val = None

        # 5. Logging en BDD
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
            "threshold_used": churn_threshold,
            "log_id": log_entry.id,
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur API : {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
