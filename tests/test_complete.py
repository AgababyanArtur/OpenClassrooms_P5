import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from main import app, get_db
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
# HELPER : Payloads Valides pour le Nouveau Modèle (10 Features)
# ==========================================


def get_valid_payload_churn():
    """Retourne un payload correspondant à un profil à risque de churn."""
    return {
        "ratio_surcharge_anciennete": 0.14,
        "nombre_participation_pee": 0,
        "statut_marital_divorce": 1.0,  # Divorcé(e) = risque
        "age": 28,  # Jeune = risque
        "annees_dans_l_entreprise": 1,  # Peu d'ancienneté = risque
        "frequence_deplacement_frequent": 1.0,  # Déplacements fréquents = risque
        "poste_representant_commercial": 1.0,  # Poste à fort turnover
        "niveau_education": 2,  # Niveau bas = risque
        "domaine_etude_marketing": 0.0,
        "poste_consultant": 0.0,
    }


def get_valid_payload_loyal():
    """Retourne un payload correspondant à un profil fidèle."""
    return {
        "ratio_surcharge_anciennete": 0.05,
        "nombre_participation_pee": 5,  # Participation PEE = engagement
        "statut_marital_divorce": 0.0,  # Pas divorcé
        "age": 50,  # Senior = plus stable
        "annees_dans_l_entreprise": 15,  # Forte ancienneté = fidèle
        "frequence_deplacement_frequent": 0.0,  # Pas de déplacements
        "poste_representant_commercial": 0.0,
        "niveau_education": 5,  # Haut niveau = engagement
        "domaine_etude_marketing": 1.0,
        "poste_consultant": 1.0,
    }


# ==========================================
# LES TESTS
# ==========================================


def test_home():
    """Vérifie que la route racine répond bien 200 et indique l'état du modèle."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "online"
    assert "model_loaded" in data


def test_prediction_workflow_churn():
    """Scénario : Un employé à risque (Churn=1)."""
    payload = get_valid_payload_churn()

    with patch("main.ml_model") as mock_model:
        # Mock du modèle pour simuler une prédiction de churn
        mock_model.predict.return_value = [1]
        mock_model.predict_proba.return_value = [[0.2, 0.8]]

        response = client.post("/predict", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == 1
        assert "probability" in data
        assert "threshold_used" in data
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
    payload = get_valid_payload_loyal()

    with patch("main.ml_model") as mock_model:
        mock_model.predict.return_value = [0]
        mock_model.predict_proba.return_value = [[0.9, 0.1]]

        response = client.post("/predict", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == 0
        assert "probability" in data
        assert data["probability"] < 0.5  # Faible risque


def test_prediction_invalid_data():
    """
    Test de Robustesse (Validation) :
    Vérifie que l'API rejette les données incorrectes.
    """
    # Payload invalide : type incorrect et champs manquants
    payload = {
        "nombre_participation_pee": 0,
        "age": "JE SUIS UNE ERREUR",  # Type invalide
        # Manque 8 champs obligatoires
    }

    response = client.post("/predict", json=payload)

    # Pydantic doit renvoyer une erreur 422
    assert response.status_code == 422
    assert "detail" in response.json()


def test_prediction_error_handling():
    """Vérifie la gestion d'erreur quand le modèle plante."""
    payload = get_valid_payload_churn()

    with patch("main.ml_model") as mock_model:
        # Force les deux méthodes à échouer
        mock_model.predict.side_effect = Exception("Boom! Modèle cassé (predict)")
        mock_model.predict_proba.side_effect = Exception("Boom! Modèle cassé (proba)")

        response = client.post("/predict", json=payload)

        # L'API doit capturer l'erreur et renvoyer 500
        assert response.status_code in [400, 500]
        assert "Erreur lors de la prédiction" in response.json()["detail"]


def test_predict_method_not_allowed():
    """
    Vérifie que l'API renvoie 405 (Method Not Allowed)
    pour une requête GET sur /predict.
    """
    response = client.get("/predict")
    assert response.status_code == 405
    assert "detail" in response.json()
