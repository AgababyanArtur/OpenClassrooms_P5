import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Imports depuis tes fichiers principaux (assure-toi d'être à la racine pour lancer)
from app import app, get_db
from database import Base, PredictionLog

from unittest.mock import patch

# ==========================================
# Configuration de la BDD de Test (En mémoire)
# ==========================================
# On utilise SQLite en mémoire pour les tests : c'est rapide et ça ne touche pas à ton PostgreSQL
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


# Fonction qui remplace la dépendance de BDD pour les tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# On applique le remplacement ("mock")
app.dependency_overrides[get_db] = override_get_db

# Client de test FastAPI
client = TestClient(app)


# Fixture : s'exécute avant chaque test pour préparer le terrain
@pytest.fixture(autouse=True)
def setup_database():
    # Crée les tables dans la BDD temporaire
    Base.metadata.create_all(bind=engine_test)
    yield
    # Nettoie après le test
    Base.metadata.drop_all(bind=engine_test)


# ==========================================
# 1. Tests Unitaires (Composants isolés)
# ==========================================


def test_home_endpoint():
    """Vérifie que l'API est en ligne"""
    response = client.get("/")
    assert response.status_code == 200
    assert "API connectée" in response.json()["message"]


def test_prediction_schema_validation():
    """Vérifie que l'API rejette les données incomplètes (Erreur 422)"""
    # On envoie un json vide
    response = client.post("/predict", json={})
    assert response.status_code == 422  # Unprocessable Entity


# ==========================================
# 2. Tests Fonctionnels (Scénarios complets)
# ==========================================


def test_prediction_workflow_churn():
    """
    Scénario : Un employé à risque (Churn=1)
    On vérifie la réponse API ET l'enregistrement en BDD.
    """
    # Données fictives simulant un départ probable
    payload = {
        "ratio_surcharge_anciennete": 0.14,
        "nombre_participation_pee": 0,
        "departement_consulting": 0.0,
        "age": 41,
        "poste_consultant": 0.0,
        "tension_salaire": 0.0003,
        "statut_marital_marie": 0.0,
        "annees_dans_l_entreprise": 0,
        "satisfaction_globale_moyenne": 2.0,
        "satisfaction_employee_nature_travail": 0,
    }

    response = client.post("/predict", json=payload)

    # 1. Vérification API
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert "log_id" in data

    # Vérifie que l'ID retourné est bien un entier
    log_id = data["log_id"]
    assert isinstance(log_id, int)

    # 2. Vérification Base de Données (La traçabilité a-t-elle fonctionné ?)
    db = TestingSessionLocal()
    log_entry = db.query(PredictionLog).filter(PredictionLog.id == log_id).first()

    assert log_entry is not None
    assert log_entry.prediction == data["prediction"]
    # Vérifie qu'on retrouve bien l'âge envoyé dans le JSON stocké
    assert log_entry.inputs["age"] == 41

    db.close()


def test_prediction_workflow_loyal():
    """
    Scénario : Un employé fidèle (Churn=0)
    Données 'inventées' pour essayer de viser 0
    """
    payload = {
        "ratio_surcharge_anciennete": 0.0,
        "nombre_participation_pee": 5,  # Participe beaucoup
        "departement_consulting": 1.0,
        "age": 50,
        "poste_consultant": 1.0,
        "tension_salaire": 0.8,
        "statut_marital_marie": 1.0,
        "annees_dans_l_entreprise": 15,
        "satisfaction_globale_moyenne": 4.0,  # Très satisfait
        "satisfaction_employee_nature_travail": 4,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200


def test_prediction_error_handling():
    """
    Test Unitaire : Vérifie que l'API gère bien les erreurs internes (500/400).
    On simule (mock) une panne du modèle pour voir si l'API survit.
    """
    # Données valides
    payload = {
        "ratio_surcharge_anciennete": 0.14,
        "nombre_participation_pee": 0,
        "departement_consulting": 0.0,
        "age": 41,
        "poste_consultant": 0.0,
        "tension_salaire": 0.0003,
        "statut_marital_marie": 0.0,
        "annees_dans_l_entreprise": 0,
        "satisfaction_globale_moyenne": 2.0,
        "satisfaction_employee_nature_travail": 0,
    }

    # On "truque" la méthode predict du modèle pour qu'elle lève une erreur
    with patch("app.model.predict", side_effect=Exception("Boom! Modèle cassé")):
        response = client.post("/predict", json=payload)

    # On s'attend à ce que l'API attrape l'erreur et renvoie 400 (selon ton code app.py)
    # Note : Dans ton app.py, le 'except' renvoie 400.
    assert response.status_code == 400
    assert "Boom! Modèle cassé" in response.json()["detail"]
