from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):
    """
    Schema base de Categoría
    """
    name: str = Field(..., min_length=1, max_length=50, description="Nombre de la categoría")
    color: str = Field(default="#3B82F6", pattern="^#[0-9A-Fa-f]{6}$", description="Color en hexadecimal")


class CategoryCreate(CategoryBase):
    """
    Schema para crear una nueva categoría
    """
    pass


class CategoryUpdate(BaseModel):
    """
    Schema para actualizar una categoría
    Todos los campos son opcionales
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class CategoryResponse(CategoryBase):
    """
    Schema para la respuesta de categoría
    """
    id: int
    user_id: int
    created_at: datetime

    class Config:
        """Configuración para que Pydantic trabaje con modelos de SQLAlchemy"""
        from_attributes = True