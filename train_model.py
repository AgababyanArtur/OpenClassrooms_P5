import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# --- CONFIGURATION ---
DATA_PATH = "final_data_set.csv"
MODEL_PATH = "model/model.pkl"  # On garde un nom standard
TARGET_COLUMN = "a_quitte_l_entreprise_num"
TEST_SIZE = 0.2
RANDOM_STATE = 42


def train_and_evaluate():
    print("1. Chargement des données...", flush=True)
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"ERREUR : Le fichier {DATA_PATH} est introuvable.")
        return

    # --- PRÉTRAITEMENT ---
    print("2. Prétraitement des données...", flush=True)

    # Séparation Features (X) et Target (y)
    y = df[TARGET_COLUMN]
    X = df.drop(TARGET_COLUMN, axis=1)

    # Encodage des variables catégorielles
    for col in X.select_dtypes(include=["object"]).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])

    # Encodage de la cible
    le_target = LabelEncoder()
    y = le_target.fit_transform(y)

    # --- SPLIT TRAIN / TEST ---
    print(f"3. Séparation des données (Test size: {TEST_SIZE})...", flush=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # --- ENTRAÎNEMENT ---
    print("4. Entraînement du modèle (Random Forest)...", flush=True)
    # Hyperparamètres robustes pour commencer
    model = RandomForestClassifier(
        n_estimators=200,  # Plus d'arbres pour la stabilité
        max_depth=15,  # Profondeur contrôlée
        min_samples_split=5,  # Évite d'apprendre par coeur des cas trop spécifiques
        class_weight="balanced",  # Gère le déséquilibre (peu de départs vs beaucoup de restes)
        random_state=RANDOM_STATE,
        n_jobs=-1,  # Utilise tous les coeurs du processeur
    )
    model.fit(X_train, y_train)

    # --- ÉVALUATION ---
    print("5. Calcul des métriques...", flush=True)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    # Affichage forcé dans la console
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DE PERFORMANCE")
    print("=" * 50)
    print(f"✅ Accuracy Globale : {acc:.2%}")
    print("\n📝 Rapport détaillé :")
    print(report)
    print("=" * 50 + "\n")

    # --- SAUVEGARDE ---
    print(f"6. Sauvegarde du modèle dans {MODEL_PATH}...", flush=True)
    joblib.dump(model, MODEL_PATH)
    print("🚀 Terminé ! Le modèle est prêt.")


if __name__ == "__main__":
    train_and_evaluate()
