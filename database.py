import os
import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ==========================================
# 1. Configuration de la connexion
# ==========================================

# Charge les variables locales (.env) si elles existent (Dev local)
load_dotenv()

# Récupère l'URL depuis l'environnement
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- MODIFICATION POUR HUGGING FACE ---
if not SQLALCHEMY_DATABASE_URL:
    # Au lieu de lever une erreur, on bascule sur une base SQLite locale
    # Cela permet à l'app de démarrer sur Hugging Face sans configuration complexe
    print("⚠️ WARNING: Variable DATABASE_URL introuvable.")
    print("🔄 Basculement automatique sur SQLite local (demo.db).")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./demo.db"
    
    # SQLite nécessite un argument spécifique pour les threads
    connect_args = {"check_same_thread": False}
else:
    print(f"✅ Connexion BDD détectée.")
    connect_args = {}

# Création du moteur
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    # Configuration spécifique SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Configuration standard PostgreSQL
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
    target_churn = Column(Integer, nullable=True)


class PredictionLog(Base):
    """
    Table pour tracer toutes les prédictions faites par l'API.
    """
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    inputs = Column(JSON)
    prediction = Column(Integer)
    probability = Column(Float)


# ==========================================
# 3. Utilitaire de Session & Init
# ==========================================

def get_db():
    """Recupère une session BDD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# IMPORTANT : Création automatique des tables si elles n'existent pas
# Cela garantit que la base SQLite locale est prête à l'emploi
Base.metadata.create_all(bind=engine)