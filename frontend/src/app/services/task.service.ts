import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Task, TaskCreate, TaskUpdate, TaskStats } from '../models';

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
    skip?: number;
    limit?: number;
  }): Observable<Task[]> {
    let params = new HttpParams();
    
    if (filters) {
      if (filters.is_completed !== undefined) {
        params = params.set('is_completed', filters.is_completed.toString());
      }
      if (filters.category_id) {
        params = params.set('category_id', filters.category_id.toString());
      }
      if (filters.priority) {
        params = params.set('priority', filters.priority);
      }
      if (filters.skip) {
        params = params.set('skip', filters.skip.toString());
      }
      if (filters.limit) {
        params = params.set('limit', filters.limit.toString());
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
   * Marcar tarea como completada
   */
  completeTask(id: number): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/${id}/complete`, {});
  }

  /**
   * Marcar tarea como pendiente
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

  /**
   * Importar tareas desde archivo Excel
   */
  importTasksFromExcel(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post(`${this.apiUrl}/import-excel`, formData);
  }

  /**
   * Descargar plantilla de Excel
   */
  downloadExcelTemplate(): void {
    const url = `${this.apiUrl}/download-template`;
    
    this.http.get(url, { responseType: 'blob', observe: 'response' }).subscribe({
      next: (response) => {
        // Crear blob desde la respuesta
        const blob = response.body;
        if (!blob) {
          console.error('No se recibió archivo');
          return;
        }

        // Crear URL temporal del blob
        const blobUrl = window.URL.createObjectURL(blob);
        
        // Crear elemento <a> temporal
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = 'plantilla_tareas.xlsx';
        
        // Agregar al DOM, hacer click y remover
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Liberar memoria
        setTimeout(() => {
          window.URL.revokeObjectURL(blobUrl);
        }, 100);
      },
      error: (error) => {
        console.error('Error descargando plantilla:', error);
        alert('❌ Error al descargar la plantilla. Verifica tu conexión.');
      }
    });
  }
}