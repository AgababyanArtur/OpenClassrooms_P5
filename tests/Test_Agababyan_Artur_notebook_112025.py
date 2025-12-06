# Fichier : tests/test_model_loading.py


# Simulation de la librairie FastAPI pour l'exemple
# Supposons qu'elle charge un modèle scikit-learn
def load_model():
    """Simule le chargement du modèle sérialisé."""
    # Ici, nous simulerons un chargement réussi en renvoyant True
    # Plus tard, vous utiliserez un outil comme joblib.load('model.pkl')
    try:
        # Tentative de charger le modèle (à remplacer par la vraie logique plus tard)
        # Pour l'instant, on s'assure que le chemin est correct et que le modèle existe
        return "Modèle chargé !"
    except FileNotFoundError:
        return "Erreur: Modèle non trouvé."


def test_model_is_loaded_correctly():
    """
    Vérifie que le modèle de Machine Learning se charge sans erreur.
    Ceci est un test critique pour le démarrage de l'API.
    """
    model_status = load_model()

    # Nous nous attendons à ce que la fonction ne retourne pas d'erreur.
    assert (
        "Erreur" not in model_status
    ), "Le modèle n'a pas pu être chargé. Vérifiez le chemin du fichier."
    assert "Modèle" in model_status, "Le statut du modèle est incorrect."

    # Vous pouvez aussi vérifier que l'objet chargé est du bon type si vous le faisiez pour de vrai.
    print(f"Statut de chargement du modèle : {model_status}")
