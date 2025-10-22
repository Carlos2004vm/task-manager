from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from auth import get_current_active_user

# Crear router para las rutas de categorías
router = APIRouter(
    prefix="/categories",
    tags=["Categorías"]
)


# ======================================= 
# ENDPOINT: OBTENER TODAS LAS CATEGORÍAS 
# =======================================
@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las categorías del usuario actual
    
    Args:
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        List[CategoryResponse]: Lista de categorías
    """
    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return categories


# =========================== 
# ENDPOINT: CREAR CATEGORÍA 
# ===========================
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva categoría
    
    Args:
        category: Datos de la categoría a crear
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        CategoryResponse: Categoría creada
        
    Raises:
        HTTPException: Si ya existe una categoría con ese nombre
    """
    # Verificar si ya existe una categoría con ese nombre para este usuario
    existing_category = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category.name
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una categoría con ese nombre"
        )
    
    # Crear nueva categoría
    db_category = Category(
        **category.model_dump(),
        user_id=current_user.id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


# ==================================== 
# ENDPOINT: OBTENER CATEGORÍA POR ID 
# ====================================
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener una categoría por ID
    
    Args:
        category_id: ID de la categoría
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        CategoryResponse: Categoría encontrada
        
    Raises:
        HTTPException: Si la categoría no existe o no pertenece al usuario
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    return category


# ================================ 
# ENDPOINT: ACTUALIZAR CATEGORÍA 
# ================================
@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar una categoría
    
    Args:
        category_id: ID de la categoría
        category_update: Datos a actualizar
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        CategoryResponse: Categoría actualizada
        
    Raises:
        HTTPException: Si la categoría no existe o el nombre ya está en uso
    """
    # Buscar categoría
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    # Verificar si el nuevo nombre ya existe
    if category_update.name and category_update.name != category.name:
        existing_category = db.query(Category).filter(
            Category.user_id == current_user.id,
            Category.name == category_update.name
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre"
            )
        category.name = category_update.name
    
    # Actualizar color si se proporciona
    if category_update.color is not None:
        category.color = category_update.color
    
    db.commit()
    db.refresh(category)
    
    return category


# ============================== 
# ENDPOINT: ELIMINAR CATEGORÍA 
# ==============================
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar una categoría
    
    Args:
        category_id: ID de la categoría
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        None
        
    Raises:
        HTTPException: Si la categoría no existe o no pertenece al usuario
    """
    # Buscar categoría
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    db.delete(category)
    db.commit()
    
    return None