import pandas as pd
import pickle
import sys
from pathlib import Path

# --- MODIFICATION ICI : Import du Random Forest ---
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
    print("🚀 Démarrage du ré-entraînement automatique (Random Forest)...")
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

    print("⚙️ Entraînement du modèle Random Forest en cours...")

    # Pipeline
    # Note : Le StandardScaler n'est pas strictement obligatoire pour les arbres,
    # mais on le garde ici pour gérer proprement l'imputation et la compatibilité future.
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[("num", numeric_transformer, TARGET_FEATURES)]
    )

    # --- MODIFICATION ICI : Utilisation de RandomForestClassifier ---
    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,  # Nombre d'arbres
                    random_state=42,  # Pour la reproductibilité
                    max_depth=None,  # Profondeur max (None = illimité)
                ),
            ),
        ]
    )

    clf.fit(X, y)

    # Sauvegarde
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    print(f"✅ SUCCÈS : Modèle Random Forest régénéré et sauvegardé dans {MODEL_PATH}")


if __name__ == "__main__":
    train()
