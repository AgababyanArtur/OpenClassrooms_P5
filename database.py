import os
import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ==========================================
# 1. Configuration de la connexion
# ==========================================

# Charge les variables contenues dans le fichier .env
load_dotenv()

# Récupère l'URL depuis l'environnement
# Si la variable n'existe pas (ex: oubli), ça renvoie None ou une valeur par défaut
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "❌ ERREUR CRITIQUE : La variable DATABASE_URL est introuvable. Vérifie ton fichier .env !"
    )

# Création du moteur (le "cerveau" de la connexion)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Création de la session (l'usine à transactions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La classe de base pour tous nos modèles (tables)
Base = declarative_base()

# ==========================================
# 2. Définition des Tables (Modèles)
# ==========================================


class EmployeeHistory(Base):
    """
    Table pour stocker le dataset d'entraînement (données historiques).
    """

    __tablename__ = "employees_history"

    id = Column(Integer, primary_key=True, index=True)

    # Tes 10 features
    ratio_surcharge_anciennete = Column(Float)
    nombre_participation_pee = Column(Integer)
    departement_consulting = Column(Float)
    age = Column(Integer)
    poste_consultant = Column(Float)
    tension_salaire = Column(Float)
    statut_marital_marie = Column(Float)
    annees_dans_l_entreprise = Column(Integer)
    satisfaction_globale_moyenne = Column(Float)
    satisfaction_employee_nature_travail = Column(Integer)

    # La cible (Target) - Peut être null si on insère des données sans connaître le résultat
    target_churn = Column(Integer, nullable=True)


class PredictionLog(Base):
    """
    Table pour tracer toutes les prédictions faites par l'API.
    """

    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Date et heure de la requête (automatique)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    # On stocke l'ensemble des inputs (features) au format JSON pour la flexibilité
    inputs = Column(JSON)

    # Le résultat du modèle
    prediction = Column(Integer)
    probability = Column(Float)


# ==========================================
# 3. Utilitaire de Session
# ==========================================


def get_db():
    """
    Fonction utilitaire pour récupérer une session de base de données,
    et la fermer automatiquement après utilisation.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
