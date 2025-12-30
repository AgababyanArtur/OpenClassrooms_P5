from database import Base, engine

# Cette commande génère le SQL "CREATE TABLE" pour tous les modèles définis
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès dans PostgreSQL !")
