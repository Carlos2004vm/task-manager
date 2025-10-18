from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class User(Base):
    """
    Modelo de Usuario
    
    Atributos:
        id: Identificador único del usuario
        username: Nombre de usuario único
        email: Correo electrónico único
        hashed_password: Contraseña encriptada con bcrypt
        full_name: Nombre completo del usuario
        is_active: Indica si el usuario está activo
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    
    Relaciones:
        tasks: Lista de tareas del usuario
        categories: Lista de categorías del usuario
    """
    __tablename__ = "users"
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones con otras tablas
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")