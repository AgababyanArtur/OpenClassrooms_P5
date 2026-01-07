import pandas as pd
import pickle
import sys
from pathlib import Path
from sklearn.linear_model import LogisticRegression
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
# Ce sont les features que le modèle va utiliser pour apprendre.
TARGET_FEATURES = [
    "ratio_surcharge_anciennete",
    "nombre_participation_pee",
    "departement_Consulting",  # Déjà présent dans le CSV
    "age",
    "poste_Consultant",  # Déjà présent dans le CSV
    "tension_salaire",
    "statut_marital_Marié(e)",  # Déjà présent dans le CSV
    "annees_dans_l_entreprise",
    "satisfaction_globale_moyenne",
    "satisfaction_employee_nature_travail",
]

# 2. Nom de la colonne cible (Target) trouvé dans ton CSV
TARGET_COLUMN = "a_quitte_l_entreprise_num"


def train():
    print("🚀 Démarrage du ré-entraînement automatique...")
    print(f"📂 Dossier de travail : {BASE_DIR}")

    # Vérification du fichier
    if not DATA_PATH.exists():
        print(f"❌ ERREUR CRITIQUE : Le fichier {DATA_PATH} est introuvable.")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"📊 Données chargées : {df.shape}")

    # --- CORRECTION MAJEURE ---
    # Ton CSV contient déjà les colonnes "statut_marital_Marié(e)", etc.
    # On ne fait PAS de renommage ici, on vérifie juste qu'elles sont là.

    # Vérification des colonnes manquantes
    missing_features = [col for col in TARGET_FEATURES if col not in df.columns]
    if missing_features:
        print(
            f"❌ ERREUR CRITIQUE : Colonnes features manquantes dans le CSV : {missing_features}"
        )
        print("   Vérifiez que le CSV contient bien les colonnes exactes.")
        sys.exit(1)

    if TARGET_COLUMN not in df.columns:
        print(f"❌ ERREUR CRITIQUE : La colonne cible '{TARGET_COLUMN}' est absente.")
        sys.exit(1)

    # Sélection des données
    X = df[TARGET_FEATURES]
    y = df[TARGET_COLUMN]

    print("⚙️ Entraînement du modèle en cours...")

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

    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(random_state=42, max_iter=1000)),
        ]
    )

    clf.fit(X, y)

    # Sauvegarde
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    print(f"✅ SUCCÈS : Modèle régénéré et sauvegardé dans {MODEL_PATH}")


if __name__ == "__main__":
    train()
