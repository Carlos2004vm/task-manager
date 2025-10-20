/**
 * Tipo de prioridad de las tareas
 */
export type Priority = 'low' | 'medium' | 'high';

/**
 * Interfaz para representar una tarea
 */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  priority: Priority;
  due_date: string | null;
  category_id: number | null;
  user_id: number;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

/**
 * Interfaz para crear una nueva tarea
 */
export interface TaskCreate {
  title: string;
  description?: string;
  priority?: Priority;
  due_date?: string;
  category_id?: number;
}

/**
 * Interfaz para actualizar una tarea
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: Priority;
  due_date?: string;
  category_id?: number;
  is_completed?: boolean;
}

/**
 * Interfaz para las estadísticas de tareas
 */
export interface TaskStats {
  total: number;
  completed: number;
  pending: number;
  overdue: number;
  by_priority: {
    high: number;
    medium: number;
    low: number;
  };
}