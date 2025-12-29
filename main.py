import uvicorn
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import datetime

# Imports de ta base de données
from database import SessionLocal, PredictionLog

# --- NOUVEL IMPORT : On récupère le modèle depuis son module dédié ---
from app.models.ml_model import ml_model

# ==========================================
# 1. Configuration de l'API
# ==========================================

# Description riche pour la documentation (Markdown supporté)
description = """
API de prédiction de churn (départ) des employés. 🚀

Cette API permet aux équipes RH d'estimer la probabilité de départ d'un collaborateur
basée sur des données historiques.

## Fonctionnalités
* **Prédiction** : Classification binaire (Départ/Reste) via un modèle de Machine Learning.
* **Traçabilité** : Chaque requête est enregistrée dans une base PostgreSQL.

## Données attendues
Les données doivent être envoyées au format JSON via l'endpoint `/predict`.
"""

app = FastAPI(
    title="Projet 5 : Churn Prediction API",
    description=description,
    version="1.0.0",
    contact={
        "name": "Artur Agababyan",
        "url": "https://github.com/AgababyanArtur/OpenClassrooms_P5",
    },
)

# Dépendance pour récupérer une session de base de données à chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 2. Définition du Schéma de Données (Pydantic)
# ==========================================


class InputData(BaseModel):
    """
    Modèle de données d'entrée avec validation et documentation intégrée.
    """

    ratio_surcharge_anciennete: float = Field(
        ...,
        description="Ratio calculé entre la charge de travail et l'ancienneté.",
        example=0.14,
    )
    nombre_participation_pee: int = Field(
        ..., description="Nombre de fois où l'employé a participé au PEE.", example=0
    )
    departement_consulting: float = Field(
        ...,
        description="Indicateur binaire (1.0 = Consulting, 0.0 = Autre).",
        example=0.0,
    )
    age: int = Field(
        ..., description="Âge de l'employé en années.", ge=18, le=100, example=41
    )
    poste_consultant: float = Field(
        ...,
        description="Indicateur binaire du poste (1.0 = Consultant).",
        example=0.0,
    )
    tension_salaire: float = Field(
        ..., description="Score de tension salariale (écart marché).", example=0.0003
    )
    statut_marital_marie: float = Field(
        ...,
        description="Statut marital (1.0 = Marié, 0.0 = Autre).",
        example=0.0,
    )
    annees_dans_l_entreprise: int = Field(
        ..., description="Nombre d'années d'ancienneté.", ge=0, example=2
    )
    satisfaction_globale_moyenne: float = Field(
        ..., description="Note moyenne de satisfaction (sur 5 ou 10).", example=2.0
    )
    satisfaction_employee_nature_travail: int = Field(
        ..., description="Note de satisfaction sur la nature du travail.", example=1
    )

    # Exemple complet visible dans Swagger UI
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
    """Route de vérification de l'état de l'API."""
    return {"message": "API connectée à PostgreSQL !"}


@app.post(
    "/predict",
    summary="Prédire le risque de churn",
    description="Cette route reçoit les données socio-professionnelles d'un employé et retourne la prédiction du modèle (0 ou 1) ainsi que la probabilité associée. La requête est enregistrée en base de données.",
    tags=["Prédiction"],
    responses={
        200: {
            "description": "Succès. Retourne la prédiction et l'ID du log.",
            "content": {
                "application/json": {
                    "example": {"prediction": 1, "probability": 0.85, "log_id": 42}
                }
            },
        },
        422: {
            "description": "Erreur de validation (données manquantes ou incorrectes)."
        },
        500: {"description": "Erreur interne (modèle non chargé ou erreur BDD)."},
    },
)
def predict(input_data: InputData, db: Session = Depends(get_db)):
    """
    Traite la demande de prédiction :
    1. Prépare les données pour le modèle (DataFrame).
    2. Lance la prédiction via le module importé.
    3. Enregistre la trace dans PostgreSQL.
    4. Retourne le résultat.
    """
    # Vérification que le modèle a bien été chargé par le module ml_model
    if ml_model is None:
        raise HTTPException(
            status_code=500, detail="Le modèle n'est pas chargé sur le serveur."
        )

    try:
        # 1. Conversion des données Pydantic en DataFrame Pandas
        data_dict = input_data.model_dump()
        df = pd.DataFrame([data_dict])

        # On renomme les colonnes pour correspondre exactement à celles attendues par le modèle
        rename_mapping = {
            "statut_marital_marie": "statut_marital_Marié(e)",
            "departement_consulting": "departement_Consulting",
            "poste_consultant": "poste_Consultant",
        }
        df = df.rename(columns=rename_mapping)

        # On s'assure de l'ordre exact des colonnes
        expected_columns = [
            "ratio_surcharge_anciennete",
            "nombre_participation_pee",
            "departement_Consulting",
            "age",
            "poste_Consultant",
            "tension_salaire",
            "statut_marital_Marié(e)",
            "annees_dans_l_entreprise",
            "satisfaction_globale_moyenne",
            "satisfaction_employee_nature_travail",
        ]

        # Vérification simple pour éviter les erreurs de colonnes manquantes
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=500, detail=f"Colonnes manquantes: {missing_cols}"
            )

        df = df[expected_columns]

        # 2. Prédiction (Utilisation de ml_model importé)
        prediction_val = int(ml_model.predict(df)[0])
        proba_val = None
        if hasattr(ml_model, "predict_proba"):
            proba_val = float(ml_model.predict_proba(df)[0][1])

        # 3. 💾 ENREGISTREMENT DANS LA BASE DE DONNÉES (LOGGING)
        log_entry = PredictionLog(
            timestamp=datetime.datetime.now(),
            inputs=data_dict,
            prediction=prediction_val,
            probability=proba_val,
        )

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        print(f"📝 Log enregistré en BDD avec l'ID : {log_entry.id}")

        # 4. Retour de la réponse
        return {
            "prediction": prediction_val,
            "probability": proba_val,
            "log_id": log_entry.id,
        }

    except Exception as e:
        print(f"❌ Erreur lors de la prédiction : {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erreur interne lors de la prédiction : {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)