from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Category(Base):
    """
    Modelo de Categoría
    
    Atributos:
        id: Identificador único de la categoría
        name: Nombre de la categoría (ej: Trabajo, Personal)
        color: Color en formato hexadecimal para la UI (ej: #3B82F6)
        user_id: ID del usuario propietario de la categoría
        created_at: Fecha de creación
    
    Relaciones:
        owner: Usuario propietario de la categoría
        tasks: Lista de tareas que pertenecen a esta categoría
    """
    __tablename__ = "categories"
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), default="#3B82F6")  # Color por defecto: azul
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones con otras tablas
    owner = relationship("User", back_populates="categories")
    tasks = relationship("Task", back_populates="category")