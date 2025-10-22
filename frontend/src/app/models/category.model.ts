/**
 * Interfaz para representar una categoría
 */
export interface Category {
  id: number;
  name: string;
  color: string;
  user_id: number;
  created_at: string;
}

/**
 * Interfaz para crear una nueva categoría
 */
export interface CategoryCreate {
  name: string;
  color: string;
}

/**
 * Interfaz para actualizar una categoría
 */
export interface CategoryUpdate {
  name?: string;
  color?: string;
}