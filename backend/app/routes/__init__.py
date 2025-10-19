"""
Módulo de rutas de la API
Importa todos los routers para registrarlos en la aplicación principal
"""
from .auth import router as auth_router
from .users import router as users_router
from .categories import router as categories_router
from .tasks import router as tasks_router

# Exportar todos los routers
__all__ = [
    "auth_router",
    "users_router",
    "categories_router",
    "tasks_router",
]