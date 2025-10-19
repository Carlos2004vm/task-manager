from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class PriorityEnum(str, enum.Enum):
    """
    Enumeración para los niveles de prioridad de las tareas
    """
    low = "low"       # Prioridad baja
    medium = "medium" # Prioridad media
    high = "high"     # Prioridad alta


class Task(Base):
    """
    Modelo de Tarea
    
    Atributos:
        id: Identificador único de la tarea
        title: Título de la tarea
        description: Descripción detallada (opcional)
        is_completed: Indica si la tarea está completada
        priority: Nivel de prioridad (low, medium, high)
        due_date: Fecha límite para completar la tarea
        user_id: ID del usuario propietario
        category_id: ID de la categoría (opcional)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
        completed_at: Fecha en que se completó la tarea
    
    Relaciones:
        owner: Usuario propietario de la tarea
        category: Categoría a la que pertenece la tarea
    """
    __tablename__ = "tasks"
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    is_completed = Column(Boolean, default=False, index=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)
    due_date = Column(Date, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relaciones con otras tablas
    owner = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")