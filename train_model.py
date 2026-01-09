import pandas as pd
import pickle
import sys
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# --- CONFIGURATION ROBUSTE ---
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "final_data_set.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "mon_modele.pkl"

# 1. Liste des colonnes EXACTES présentes dans ton CSV final_data_set.csv
TARGET_FEATURES = [
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

# 2. Nom de la colonne cible
TARGET_COLUMN = "a_quitte_l_entreprise_num"


def train():
    print("🚀 Démarrage du ré-entraînement (Random Forest Optimisé)...")
    print(f"📂 Dossier de travail : {BASE_DIR}")

    # Vérification du fichier
    if not DATA_PATH.exists():
        print(f"❌ ERREUR CRITIQUE : Le fichier {DATA_PATH} est introuvable.")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"📊 Données chargées : {df.shape}")

    # Vérification des colonnes manquantes
    missing_features = [col for col in TARGET_FEATURES if col not in df.columns]
    if missing_features:
        print(f"❌ ERREUR CRITIQUE : Colonnes features manquantes : {missing_features}")
        sys.exit(1)

    if TARGET_COLUMN not in df.columns:
        print(f"❌ ERREUR CRITIQUE : La colonne cible '{TARGET_COLUMN}' est absente.")
        sys.exit(1)

    # Sélection des données
    X = df[TARGET_FEATURES]
    y = df[TARGET_COLUMN]

    print("⚙️ Entraînement avec les meilleurs hyperparamètres...")

    # Pipeline
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[("num", numeric_transformer, TARGET_FEATURES)]
    )

    # --- MODIFICATION ICI : Insertion de tes hyperparamètres ---
    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,  # Augmenté à 200 arbres
                    max_depth=10,  # Limite la profondeur pour éviter l'overfitting
                    min_samples_split=5,  # Minimum d'échantillons pour diviser un nœud
                    random_state=42,  # Toujours fixé pour la reproductibilité
                ),
            ),
        ]
    )

    clf.fit(X, y)

    # Sauvegarde
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    print(f"✅ SUCCÈS : Modèle optimisé sauvegardé dans {MODEL_PATH}")


if __name__ == "__main__":
    train()
