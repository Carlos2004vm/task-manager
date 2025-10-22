from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.user import UserResponse, UserUpdate
from auth import get_current_active_user, get_password_hash

# Crear router para las rutas de usuarios
router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)


# ================================= 
# ENDPOINT: OBTENER USUARIO ACTUAL 
# =================================
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        UserResponse: Información del usuario
    """
    return current_user


# ==================================== 
# ENDPOINT: ACTUALIZAR USUARIO ACTUAL 
# ====================================
@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar información del usuario actual
    
    Args:
        user_update: Datos a actualizar
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        UserResponse: Usuario actualizado
        
    Raises:
        HTTPException: Si el username o email ya existen
    """
    # Verificar si el nuevo username ya existe (si se proporciona)
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        current_user.username = user_update.username
    
    # Verificar si el nuevo email ya existe (si se proporciona)
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso"
            )
        current_user.email = user_update.email
    
    # Actualizar otros campos
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ================================== 
# ENDPOINT: ELIMINAR USUARIO ACTUAL 
# ==================================
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar la cuenta del usuario actual
    
    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        None
    """
    db.delete(current_user)
    db.commit()
    
    return None