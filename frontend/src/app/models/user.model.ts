/**
 * Interfaz para representar un usuario en el sistema
 */
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;

  // ✅ Campos opcionales usados en SettingsComponent
  phone?: string;
  bio?: string;
  profile_picture?: string;
}

/**
 * Interfaz para el registro de un nuevo usuario
 */
export interface UserRegister {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

/**
 * Interfaz para el login
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * Interfaz para la respuesta del token JWT
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
}
