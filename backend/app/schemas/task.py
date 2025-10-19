from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from models.task import PriorityEnum


class TaskBase(BaseModel):
    """
    Schema base de Tarea
    """
    title: str = Field(..., min_length=1, max_length=200, description="Título de la tarea")
    description: Optional[str] = Field(None, description="Descripción detallada")
    priority: PriorityEnum = Field(default=PriorityEnum.medium, description="Nivel de prioridad")
    due_date: Optional[date] = Field(None, description="Fecha límite")
    category_id: Optional[int] = Field(None, description="ID de la categoría")


class TaskCreate(TaskBase):
    """
    Schema para crear una nueva tarea
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schema para actualizar una tarea
    Todos los campos son opcionales
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[date] = None
    category_id: Optional[int] = None
    is_completed: Optional[bool] = None


class TaskResponse(TaskBase):
    """
    Schema para la respuesta de tarea
    """
    id: int
    is_completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        """Configuración para que Pydantic trabaje con modelos de SQLAlchemy"""
        from_attributes = True