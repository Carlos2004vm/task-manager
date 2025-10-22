from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
from io import BytesIO

from database import get_db
from models.user import User
from models.task import Task
from models.category import Category
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from auth import get_current_active_user

# Crear router para las rutas de tareas
router = APIRouter(
    prefix="/tasks",
    tags=["Tareas"]
)


# ==================================== 
# ENDPOINT: OBTENER TODAS LAS TAREAS 
# ====================================
@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    is_completed: Optional[bool] = None,
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las tareas del usuario actual con filtros opcionales
    
    Args:
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        is_completed: Filtrar por estado (completada o no)
        category_id: Filtrar por categoría
        priority: Filtrar por prioridad (low, medium, high)
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        List[TaskResponse]: Lista de tareas
    """
    # Query base
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    # Aplicar filtros opcionales
    if is_completed is not None:
        query = query.filter(Task.is_completed == is_completed)
    
    if category_id is not None:
        query = query.filter(Task.category_id == category_id)
    
    if priority is not None:
        query = query.filter(Task.priority == priority)
    
    # Ordenar por fecha de creación (más recientes primero)
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    return tasks


# ======================= 
# ENDPOINT: CREAR TAREA 
# =======================
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva tarea
    
    Args:
        task: Datos de la tarea a crear
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        TaskResponse: Tarea creada
    """
    # Crear nueva tarea
    db_task = Task(
        **task.model_dump(),
        user_id=current_user.id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


# ================================ 
# ENDPOINT: OBTENER TAREA POR ID 
# ================================
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener una tarea por ID
    
    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        TaskResponse: Tarea encontrada
        
    Raises:
        HTTPException: Si la tarea no existe o no pertenece al usuario
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return task


# ============================ 
# ENDPOINT: ACTUALIZAR TAREA 
# ============================
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar una tarea
    
    Args:
        task_id: ID de la tarea
        task_update: Datos a actualizar
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        TaskResponse: Tarea actualizada
        
    Raises:
        HTTPException: Si la tarea no existe o no pertenece al usuario
    """
    # Buscar tarea
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    # Actualizar campos proporcionados
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Si se marca como completada, registrar la fecha
    if task_update.is_completed is not None:
        if task_update.is_completed and not task.is_completed:
            task.completed_at = datetime.utcnow()
        elif not task_update.is_completed and task.is_completed:
            task.completed_at = None
    
    db.commit()
    db.refresh(task)
    
    return task


# ======================================== 
# ENDPOINT: MARCAR TAREA COMO COMPLETADA 
# ========================================
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Marcar una tarea como completada
    
    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        TaskResponse: Tarea actualizada
        
    Raises:
        HTTPException: Si la tarea no existe o no pertenece al usuario
    """
    # Buscar tarea
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    # Marcar como completada
    task.is_completed = True
    task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return task


# ======================================= 
# ENDPOINT: MARCAR TAREA COMO PENDIENTE 
# =======================================
@router.patch("/{task_id}/incomplete", response_model=TaskResponse)
async def incomplete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Marcar una tarea como pendiente (no completada)
    
    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        TaskResponse: Tarea actualizada
        
    Raises:
        HTTPException: Si la tarea no existe o no pertenece al usuario
    """
    # Buscar tarea
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    # Marcar como pendiente
    task.is_completed = False
    task.completed_at = None
    
    db.commit()
    db.refresh(task)
    
    return task


# ========================== 
# ENDPOINT: ELIMINAR TAREA 
# ==========================
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar una tarea
    
    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        None
        
    Raises:
        HTTPException: Si la tarea no existe o no pertenece al usuario
    """
    # Buscar tarea
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    db.delete(task)
    db.commit()
    
    return None


# ================================ 
# ENDPOINT: OBTENER ESTADÍSTICAS 
# ================================
@router.get("/stats/summary", response_model=dict)
async def get_task_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de las tareas del usuario
    
    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        dict: Estadísticas de tareas (total, completadas, pendientes, por prioridad)
    """
    # Total de tareas
    total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
    
    # Tareas completadas
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.is_completed == True
    ).count()
    
    # Tareas pendientes
    pending_tasks = total_tasks - completed_tasks
    
    # Tareas por prioridad
    high_priority = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.priority == "high",
        Task.is_completed == False
    ).count()
    
    medium_priority = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.priority == "medium",
        Task.is_completed == False
    ).count()
    
    low_priority = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.priority == "low",
        Task.is_completed == False
    ).count()
    
    # Tareas vencidas (fecha límite pasada y no completadas)
    today = date.today()
    overdue_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.is_completed == False,
        Task.due_date < today
    ).count()
    
    return {
        "total": total_tasks,
        "completed": completed_tasks,
        "pending": pending_tasks,
        "overdue": overdue_tasks,
        "by_priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        }
    }


# ================================ 
# ENDPOINT: IMPORTAR DESDE EXCEL 
# ================================
@router.post("/import-excel")
async def import_tasks_from_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Importar tareas desde archivo Excel
    
    Formato esperado del Excel:
    - title (obligatorio): Título de la tarea
    - description (opcional): Descripción
    - priority (opcional): low, medium o high
    - due_date (opcional): Formato YYYY-MM-DD
    - category_name (opcional): Nombre de la categoría existente
    
    Args:
        file: Archivo Excel (.xlsx o .xls)
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        dict: Resumen de importación (tareas creadas y errores)
    """
    # Validar extensión del archivo
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos Excel (.xlsx, .xls)"
        )
    
    try:
        # Leer archivo Excel
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # Validar que tenga columnas
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo Excel está vacío"
            )
        
        # Validar columna obligatoria
        if 'title' not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe contener al menos la columna 'title'"
            )
        
        tasks_created = []
        errors = []
        
        # Procesar cada fila
        for index, row in df.iterrows():
            try:
                # Validar título
                if pd.isna(row['title']) or str(row['title']).strip() == '':
                    errors.append(f"Fila {index + 2}: El título es obligatorio")
                    continue
                
                title = str(row['title']).strip()
                
                # Procesar descripción
                description = None
                if 'description' in df.columns and pd.notna(row['description']):
                    description = str(row['description']).strip()
                
                # Procesar prioridad
                priority = 'medium'
                if 'priority' in df.columns and pd.notna(row['priority']):
                    priority_value = str(row['priority']).lower().strip()
                    if priority_value in ['low', 'medium', 'high']:
                        priority = priority_value
                    else:
                        errors.append(f"Fila {index + 2}: Prioridad inválida '{row['priority']}'. Se usará 'medium'")
                
                # Procesar fecha límite
                due_date = None
                if 'due_date' in df.columns and pd.notna(row['due_date']):
                    try:
                        if isinstance(row['due_date'], str):
                            due_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                        else:
                            due_date = pd.to_datetime(row['due_date']).date()
                    except Exception as e:
                        errors.append(f"Fila {index + 2}: Fecha inválida '{row['due_date']}'. Se omitirá la fecha")
                
                # Buscar categoría si existe
                category_id = None
                if 'category_name' in df.columns and pd.notna(row['category_name']):
                    category_name = str(row['category_name']).strip()
                    category = db.query(Category).filter(
                        Category.name == category_name,
                        Category.user_id == current_user.id
                    ).first()
                    
                    if category:
                        category_id = category.id
                    else:
                        errors.append(f"Fila {index + 2}: Categoría '{category_name}' no encontrada. Se creará sin categoría")
                
                # Crear tarea
                new_task = Task(
                    title=title,
                    description=description,
                    priority=priority,
                    due_date=due_date,
                    user_id=current_user.id,
                    category_id=category_id,
                    is_completed=False
                )
                
                db.add(new_task)
                tasks_created.append(title)
                
            except Exception as e:
                errors.append(f"Fila {index + 2}: Error al procesar - {str(e)}")
        
        # Confirmar cambios en la base de datos
        db.commit()
        
        return {
            "success": True,
            "message": "Importación completada",
            "tasks_created": len(tasks_created),
            "tasks_list": tasks_created[:10],  # Mostrar solo las primeras 10
            "total_rows": len(df),
            "errors_count": len(errors),
            "errors": errors[:10]  # Mostrar solo los primeros 10 errores
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo Excel está vacío o corrupto"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando archivo: {str(e)}"
        )


# ======================================= 
# ENDPOINT: DESCARGAR PLANTILLA EXCEL 
# =======================================
@router.get("/download-template")
async def download_excel_template(
    current_user: User = Depends(get_current_active_user)
):
    """
    Descargar plantilla Excel para importar tareas
    
    Returns:
        StreamingResponse: Archivo Excel con estructura de ejemplo
    """
    # Crear DataFrame con estructura de ejemplo
    # Crear DataFrame con TUS datos personalizados
    template_data = {
        'title': [
            'Tarea 1',
            'Tarea 2',
            'Tarea 3',
            'Tarea 4',
            'Tarea 5',
            'Tarea 6',
            'Tarea 7'
        ],
        'description': [
            'Entregar Antes del 12',
            'Hacerla antes del 10',
            'Antes que terminen',
            'Entregar Antes del 13',
            'Hacerla antes del 11',
            'Antes que terminen',
            'Entregar Antes del 14'
        ],
        'priority': ['medium', 'low', 'high', 'medium', 'low', 'high', 'medium'],
        'due_date': [
            '2025-12-31',
            '2026-01-01',
            '2026-01-02',
            '2026-01-03',
            '2026-01-04',
            '2026-01-05',
            '2026-01-06'
        ],
    }
    
    df = pd.DataFrame(template_data)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tareas')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_tareas.xlsx"}
    )