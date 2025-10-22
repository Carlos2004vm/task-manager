"""
Módulo de schemas de Pydantic
Importa todos los schemas para facilitar su uso
"""
from .user import UserBase, UserCreate, UserUpdate, UserResponse
from .category import CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse
from .task import TaskBase, TaskCreate, TaskUpdate, TaskResponse
from .auth import Token, TokenData, LoginRequest

# Exportar todos los schemas
__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Category schemas
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # Task schemas
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    # Auth schemas
    "Token",
    "TokenData",
    "LoginRequest",
]