import pandas as pd
from database import SessionLocal, engine, Base, EmployeeHistory

CSV_PATH = "final_data_set.csv"


def init_database():
    # Création des tables
    Base.metadata.create_all(bind=engine)

    print(f"📂 Lecture du fichier {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {CSV_PATH} est introuvable.")
        return

    # --- MAPPING CSV VERS BASE DE DONNÉES ---
    # Clé = Nom dans le CSV (compliqué)
    # Valeur = Nom dans la BDD (propre, défini dans database.py)
    rename_mapping = {
        "statut_marital_Marié(e)": "statut_marital_marie",
        "departement_Consulting": "departement_consulting",
        "poste_Consultant": "poste_consultant",
        "a_quitte_l_entreprise_num": "target_churn",  # <-- Correction ici
    }

    # On renomme les colonnes du DataFrame pour qu'elles collent au modèle SQLAlchemy
    df = df.rename(columns=rename_mapping)

    # Liste des colonnes attendues par la table EmployeeHistory
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

    # Remplissage des manquants par 0
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0

    df = df.fillna(0)

    session = SessionLocal()
    try:
        session.query(EmployeeHistory).delete()
        print("💾 Insertion des données en cours...")

        data_to_insert = []
        for _, row in df.iterrows():
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
        print(f"✅ Succès ! {len(data_to_insert)} employés insérés.")

    except Exception as e:
        session.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
