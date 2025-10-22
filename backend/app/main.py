from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from database import engine, Base
from routes import auth_router, users_router, categories_router, tasks_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Task Manager API",
    description="API REST para gestión de tareas con autenticación JWT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ======================= 
# CONFIGURACIÓN DE CORS 
# =======================

# Permitir peticiones desde el frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular en desarrollo
        "http://localhost",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],  # Permitir todos los headers
)


# ==================== 
# ENDPOINT: RAÍZ 
# ====================
@app.get("/")
async def root():
    """
    Endpoint raíz de la API
    
    Returns:
        dict: Mensaje de bienvenida
    """
    return {
        "message": "Task Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


# ======================== 
# ENDPOINT: HEALTH CHECK 
# ========================
@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API
    
    Returns:
        dict: Estado de la API
    """
    return {
        "status": "healthy",
        "database": "connected"
    }


# ==================== 
# REGISTRAR ROUTERS 
# ====================

# Incluir todos los routers de la aplicación
app.include_router(auth_router)      # Rutas de autenticación
app.include_router(users_router)     # Rutas de usuarios
app.include_router(categories_router) # Rutas de categorías
app.include_router(tasks_router)     # Rutas de tareas

logger.info("✅ Aplicación FastAPI iniciada correctamente")
logger.info("📚 Documentación disponible en: http://localhost:8001/docs")
logger.info("🔄 Redoc disponible en: http://localhost:8001/redoc")


# ==================== 
# EVENTO: STARTUP 
# ====================
@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación
    """
    logger.info("🚀 Iniciando Task Manager API...")
    logger.info("📊 Base de datos: MySQL")
    logger.info("🔐 Autenticación: JWT")
    logger.info("✨ CORS configurado para Angular")


# ==================== 
# EVENTO: SHUTDOWN 
# ====================
@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento que se ejecuta al cerrar la aplicación
    """
    logger.info("👋 Cerrando Task Manager API...")