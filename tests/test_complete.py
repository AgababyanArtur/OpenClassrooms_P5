import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

# Imports depuis tes fichiers principaux
from app import app, get_db
from database import Base, PredictionLog

# ==========================================
# Configuration de la BDD de Test (SQLite en mémoire)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Crée les tables avant chaque test et les supprime après."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


# ==========================================
# LES TESTS
# ==========================================


def test_home():
    """Vérifie que la route racine répond bien 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API connectée à PostgreSQL !"}


def test_prediction_workflow_churn():
    """Scénario : Un employé à risque (Churn=1)."""
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

    with patch("app.model") as mock_model:
        mock_model.predict.return_value = [1]
        mock_model.predict_proba.return_value = [[0.2, 0.8]]

        response = client.post("/predict", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == 1
        assert "log_id" in data

        # Vérification BDD
        log_id = data["log_id"]
        db = TestingSessionLocal()
        log_entry = db.query(PredictionLog).filter(PredictionLog.id == log_id).first()
        assert log_entry is not None
        assert log_entry.prediction == 1
        db.close()


def test_prediction_workflow_loyal():
    """Scénario : Un employé fidèle (Churn=0)."""
    payload = {
        "ratio_surcharge_anciennete": 0.0,
        "nombre_participation_pee": 5,
        "departement_consulting": 1.0,
        "age": 50,
        "poste_consultant": 1.0,
        "tension_salaire": 0.8,
        "statut_marital_marie": 1.0,
        "annees_dans_l_entreprise": 15,
        "satisfaction_globale_moyenne": 4.0,
        "satisfaction_employee_nature_travail": 4,
    }

    with patch("app.model") as mock_model:
        mock_model.predict.return_value = [0]
        mock_model.predict_proba.return_value = [[0.9, 0.1]]

        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        assert response.json()["prediction"] == 0


def test_prediction_invalid_data():
    """
    Test de Robustesse (Validation) :
    Vérifie que l'API rejette les données incorrectes (ex: string au lieu de int).
    """
    # Payload invalide : 'age' est une chaîne de caractères, 'ratio' manquant
    payload = {
        "nombre_participation_pee": 0,
        "departement_consulting": 0.0,
        "age": "JE SUIS UNE ERREUR",  # <--- Erreur de type
        "poste_consultant": 0.0,
        # Manque plein de champs obligatoires
    }

    response = client.post("/predict", json=payload)

    # Pydantic doit renvoyer une erreur 422 (Unprocessable Entity)
    assert response.status_code == 422
    # On vérifie que l'erreur concerne bien les champs manquants ou invalides
    assert "detail" in response.json()


def test_prediction_error_handling():
    """Vérifie la gestion d'erreur quand le modèle plante."""
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

    with patch("app.model") as mock_model:
        # On force le modèle à planter
        mock_model.predict.side_effect = Exception("Boom! Modèle cassé")

        response = client.post("/predict", json=payload)

        # On accepte 400 ou 500 selon la gestion d'erreur dans app.py
        assert response.status_code in [400, 500]
        assert "detail" in response.json()
