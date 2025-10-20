import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Task, TaskCreate, TaskUpdate, TaskStats } from '../models';

/**
 * Servicio para gestión de tareas
 */
@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private apiUrl = `${environment.apiUrl}/tasks`;

  constructor(private http: HttpClient) {}

  /**
   * Obtener todas las tareas con filtros opcionales
   */
  getTasks(filters?: {
    is_completed?: boolean;
    category_id?: number;
    priority?: string;
  }): Observable<Task[]> {
    let params = new HttpParams();
    
    if (filters) {
      if (filters.is_completed !== undefined) {
        params = params.set('is_completed', filters.is_completed.toString());
      }
      if (filters.category_id !== undefined) {
        params = params.set('category_id', filters.category_id.toString());
      }
      if (filters.priority) {
        params = params.set('priority', filters.priority);
      }
    }

    return this.http.get<Task[]>(this.apiUrl, { params });
  }

  /**
   * Obtener una tarea por ID
   */
  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.apiUrl}/${id}`);
  }

  /**
   * Crear una nueva tarea
   */
  createTask(task: TaskCreate): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, task);
  }

  /**
   * Actualizar una tarea
   */
  updateTask(id: number, task: TaskUpdate): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${id}`, task);
  }

  /**
   * Marcar una tarea como completada
   */
  completeTask(id: number): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/${id}/complete`, {});
  }

  /**
   * Marcar una tarea como pendiente
   */
  incompleteTask(id: number): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/${id}/incomplete`, {});
  }

  /**
   * Eliminar una tarea
   */
  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  /**
   * Obtener estadísticas de tareas
   */
  getStats(): Observable<TaskStats> {
    return this.http.get<TaskStats>(`${this.apiUrl}/stats/summary`);
  }
}