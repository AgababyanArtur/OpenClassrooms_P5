from fastapi.testclient import TestClient
from app import app  # On importe l'objet 'app' de ton fichier app.py

# Création du client de test simulé
client = TestClient(app)


def test_home():
    """Vérifie que la route racine répond bien 200"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "API fonctionnelle ! Va sur /docs pour tester la prédiction."
    }


def test_predict_valid():
    """Vérifie qu'une prédiction fonctionne avec des données correctes"""
    # Un exemple de données valides (basé sur ton X_test réduit)
    payload = {
        "ratio_surcharge_anciennete": 10.5,
        "nombre_participation_pee": 2,
        "departement_consulting": 1.0,
        "age": 34,
        "poste_consultant": 1.0,
        "tension_salaire": 0.5,
        "statut_marital_marie": 1.0,
        "annees_dans_l_entreprise": 5,
        "satisfaction_globale_moyenne": 0.7,
        "satisfaction_employee_nature_travail": 1,
    }

    response = client.post("/predict", json=payload)

    # Vérifications
    assert response.status_code == 200
    json_data = response.json()
    assert "prediction" in json_data
    assert "probability" in json_data
    # La prédiction doit être 0 ou 1
    assert json_data["prediction"] in [0, 1]


def test_predict_invalid_data():
    """Vérifie que l'API rejette des données manquantes (Erreur 422)"""
    # Payload incomplet (il manque 'age', 'poste_consultant', etc.)
    payload = {"ratio_surcharge_anciennete": 10.5}

    response = client.post("/predict", json=payload)

    # FastAPI renvoie automatiquement 422 (Unprocessable Entity) si le schéma Pydantic n'est pas respecté
    assert response.status_code == 422
