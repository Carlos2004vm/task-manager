from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener la URL de conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el engine de SQLAlchemy (motor de conexión)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_recycle=3600    # Reciclar conexiones cada hora
)

# Crear una clase SessionLocal para manejar sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos de SQLAlchemy
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
def get_db():
    """
    Generador que proporciona una sesión de base de datos
    y la cierra automáticamente al terminar
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()