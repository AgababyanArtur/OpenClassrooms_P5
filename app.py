import uvicorn
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import datetime

# Imports de ta base de données
from database import SessionLocal, engine, PredictionLog

# ==========================================
# 1. Configuration et Chargement
# ==========================================

app = FastAPI(
    title="API de Prédiction - Projet 5",
    description="API avec traçabilité dans PostgreSQL.",
    version="1.0.0"
)

MODEL_PATH = "model/mon_modele.joblib"

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle chargé avec succès depuis {MODEL_PATH}")
except Exception as e:
    print(f"❌ ERREUR : Impossible de charger le modèle : {e}")
    model = None

# Dépendance pour récupérer une session de base de données à chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. Définition du Schéma de Données
# ==========================================

class InputData(BaseModel):
    ratio_surcharge_anciennete: float
    nombre_participation_pee: int
    departement_consulting: float
    age: int
    poste_consultant: float
    tension_salaire: float
    statut_marital_marie: float
    annees_dans_l_entreprise: int
    satisfaction_globale_moyenne: float
    satisfaction_employee_nature_travail: int

# ==========================================
# 3. Endpoints
# ==========================================

@app.get("/")
def home():
    return {"message": "API connectée à PostgreSQL !"}

@app.post("/predict")
def predict(data: InputData, db: Session = Depends(get_db)):
    """
    Reçoit les données, fait une prédiction, et SAUVEGARDE tout dans la BDD.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé.")

    try:
        # 1. Préparation des données pour le modèle
        input_data = data.model_dump()
        df = pd.DataFrame([input_data])

        # Renommage pour coller au modèle
        rename_dict = {
            "departement_consulting": "departement_Consulting",
            "poste_consultant": "poste_Consultant",
            "statut_marital_marie": "statut_marital_Marié(e)"
        }
        df = df.rename(columns=rename_dict)
        
        # Réorganisation des colonnes
        expected_columns = [
            "ratio_surcharge_anciennete", "nombre_participation_pee", 
            "departement_Consulting", "age", "poste_Consultant", 
            "tension_salaire", "statut_marital_Marié(e)", 
            "annees_dans_l_entreprise", "satisfaction_globale_moyenne", 
            "satisfaction_employee_nature_travail"
        ]
        df = df[expected_columns]

        # 2. Prédiction
        prediction_val = int(model.predict(df)[0])
        proba_val = None
        if hasattr(model, "predict_proba"):
            proba_val = float(model.predict_proba(df)[0][1])

        # 3. 💾 ENREGISTREMENT DANS LA BASE DE DONNÉES (LOGGING)
        # On stocke les inputs bruts au format JSON pour la traçabilité
        log_entry = PredictionLog(
            timestamp=datetime.datetime.now(),
            inputs=input_data,  # SQLAlchemy convertira auto le dict en JSON
            prediction=prediction_val,
            probability=proba_val
        )
        
        db.add(log_entry)
        db.commit() # On valide l'enregistrement
        db.refresh(log_entry) # On récupère l'ID généré

        print(f"📝 Log enregistré en BDD avec l'ID : {log_entry.id}")

        # 4. Retour de la réponse
        return {
            "prediction": prediction_val,
            "probability": proba_val,
            "log_id": log_entry.id # On renvoie l'ID du log pour preuve
        }

    except Exception as e:
        print(f"Erreur : {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)