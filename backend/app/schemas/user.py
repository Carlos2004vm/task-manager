from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Schema base de Usuario (campos comunes)
    """
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Correo electrónico válido")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo")


class UserCreate(UserBase):
    """
    Schema para crear un nuevo usuario
    Incluye la contraseña en texto plano (se encriptará en el backend)
    """
password: str = Field(..., min_length=6, max_length=72, description="Contraseña (mínimo 6, máximo 72 caracteres)")


class UserUpdate(BaseModel):
    """
    Schema para actualizar un usuario
    Todos los campos son opcionales
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    Schema para la respuesta de usuario
    No incluye la contraseña por seguridad
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuración para que Pydantic trabaje con modelos de SQLAlchemy"""
        from_attributes = True