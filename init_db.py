import pandas as pd
from database import SessionLocal, engine, Base, EmployeeHistory

# ==========================================
# Configuration
# ==========================================
CSV_PATH = "final_data_set.csv"


def init_database():
    # 1. Création des tables
    Base.metadata.create_all(bind=engine)

    # 2. Chargement du CSV
    print(f"📂 Lecture du fichier {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"✅ Fichier chargé : {len(df)} lignes trouvées.")
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {CSV_PATH} est introuvable.")
        return

    # 3. Nettoyage et Mapping des colonnes
    rename_mapping = {
        "statut_marital_Marié(e)": "statut_marital_marie",
        "departement_Consulting": "departement_consulting",
        "poste_Consultant": "poste_consultant",
        "a_quitte_l_entreprise_num": "target_churn",
    }
    df = df.rename(columns=rename_mapping)

    # 4. Vérification des colonnes manquantes
    expected_columns = [
        "ratio_surcharge_anciennete",
        "nombre_participation_pee",
        "departement_consulting",
        "age",
        "poste_consultant",
        "tension_salaire",
        "statut_marital_marie",
        "annees_dans_l_entreprise",
        "satisfaction_globale_moyenne",
        "satisfaction_employee_nature_travail",
        "target_churn",
    ]

    for col in expected_columns:
        if col not in df.columns:
            print(f"⚠️ Attention : La colonne '{col}' est absente. Remplacement par 0.")
            df[col] = 0

    # 5. Remplacer les NaN par 0 (pour éviter les erreurs de conversion int)
    df = df.fillna(0)

    # 6. Insertion en base de données
    session = SessionLocal()
    try:
        # On vide la table avant de remplir (Optionnel)
        session.query(EmployeeHistory).delete()

        print("💾 Insertion des données en cours...")

        data_to_insert = []
        for _, row in df.iterrows():
            # 🚨 C'est ICI que la magie opère :
            # On utilise float() et int() pour convertir les types numpy en types Python purs
            employee = EmployeeHistory(
                ratio_surcharge_anciennete=float(row["ratio_surcharge_anciennete"]),
                nombre_participation_pee=int(row["nombre_participation_pee"]),
                departement_consulting=float(row["departement_consulting"]),
                age=int(row["age"]),
                poste_consultant=float(row["poste_consultant"]),
                tension_salaire=float(row["tension_salaire"]),
                statut_marital_marie=float(row["statut_marital_marie"]),
                annees_dans_l_entreprise=int(row["annees_dans_l_entreprise"]),
                satisfaction_globale_moyenne=float(row["satisfaction_globale_moyenne"]),
                satisfaction_employee_nature_travail=int(
                    row["satisfaction_employee_nature_travail"]
                ),
                target_churn=int(row["target_churn"]),
            )
            data_to_insert.append(employee)

        session.add_all(data_to_insert)
        session.commit()
        print(f"✅ Succès ! {len(data_to_insert)} employés ont été insérés dans PostgreSQL.")

    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de l'insertion : {e}")
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
