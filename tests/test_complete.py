import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

# Imports depuis tes fichiers principaux
from app import app, get_db

# 1. On n'oublie pas d'importer PredictionLog pour la vérification BDD !
from database import Base, PredictionLog

# ==========================================
# Configuration de la BDD de Test (SQLite en mémoire)
# ==========================================
# Utilisation d'une BDD temporaire pour isoler les tests
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


# Remplacement de la dépendance BDD
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
    # On s'assure que le message correspond à celui de ton app.py
    assert response.json() == {"message": "API connectée à PostgreSQL !"}


def test_prediction_workflow_churn():
    """
    Scénario : Un employé à risque (Churn=1).
    Test robuste grâce au mocking de l'objet 'model' entier.
    """
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

    # 2. PATCH ROBUSTE : On remplace tout l'objet 'app.model' par un Mock
    # Cela évite l'erreur si app.model est None (fichier non chargé)
    with patch("app.model") as mock_model:
        # Configuration du faux modèle
        mock_model.predict.return_value = [1]
        mock_model.predict_proba.return_value = [[0.2, 0.8]]

        response = client.post("/predict", json=payload)

        # Vérifications API
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == 1
        assert "log_id" in data

        # Vérification BDD (Traçabilité)
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


def test_prediction_error_handling():
    """
    Vérifie la gestion d'erreur quand le modèle plante.
    C'est ici que l'erreur 'None attribute' se produisait avant correction.
    """
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

    # 3. MÊME CORRECTION : On patch l'objet entier, pas la méthode
    # L'erreur venait de patch("app.model.predict") qui plantait car model était None
    with patch("app.model") as mock_model:
        # On force le modèle à planter
        mock_model.predict.side_effect = Exception("Boom! Modèle cassé")

        response = client.post("/predict", json=payload)

        assert response.status_code == 500
        assert "Erreur interne" in response.json()["detail"]
