from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
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
# ===================================
# ENDPOINT: ACTUALIZAR PERFIL
# ===================================
@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar información del perfil del usuario actual
    """
    # Actualizar solo los campos proporcionados
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Si se proporciona nueva contraseña, hashearla
    if "password" in update_data:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ===================================
# ENDPOINT: SUBIR FOTO DE PERFIL
# ===================================
@router.post("/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Subir o actualizar foto de perfil
    """
    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imágenes (JPEG, PNG, WEBP)"
        )
    
    # Validar tamaño (máximo 5MB)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La imagen no debe superar 5MB"
            )
    
    # Volver al inicio del archivo
    await file.seek(0)
    
    # Generar nombre único para el archivo
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{current_user.id}_{uuid.uuid4()}.{file_extension}"
    
    # Crear directorio si no existe
    upload_dir = Path("/app/uploads/profiles")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar archivo
    file_path = upload_dir / unique_filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Eliminar foto anterior si existe
    if current_user.profile_picture:
        old_file = Path(current_user.profile_picture)
        if old_file.exists():
            old_file.unlink()
    
    # Actualizar ruta en base de datos
    current_user.profile_picture = str(file_path)
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "message": "Foto de perfil actualizada",
        "filename": unique_filename,
        "url": f"/users/me/profile-picture/{unique_filename}"
    }


# ===================================
# ENDPOINT: OBTENER FOTO DE PERFIL
# ===================================
@router.get("/me/profile-picture/{filename}")
async def get_profile_picture(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener foto de perfil del usuario
    """
    file_path = Path(f"/app/uploads/profiles/{filename}")
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foto de perfil no encontrada"
        )
    
    return FileResponse(file_path)


# ===================================
# ENDPOINT: ELIMINAR FOTO DE PERFIL
# ===================================
@router.delete("/me/profile-picture")
async def delete_profile_picture(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar foto de perfil
    """
    if not current_user.profile_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay foto de perfil para eliminar"
        )
    
    # Eliminar archivo
    file_path = Path(current_user.profile_picture)
    if file_path.exists():
        file_path.unlink()
    
    # Actualizar base de datos
    current_user.profile_picture = None
    db.commit()
    
    return {"success": True, "message": "Foto de perfil eliminada"}