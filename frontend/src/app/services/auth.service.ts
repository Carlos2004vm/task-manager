import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { User, UserRegister, LoginRequest, TokenResponse } from '../models';

/**
 * Servicio de autenticación
 * Maneja login, registro, tokens y estado del usuario actual
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  
  // Observable público del usuario actual
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Al iniciar, verificar si hay un usuario guardado en localStorage
    this.loadUserFromStorage();
  }

  /**
   * Cargar usuario desde localStorage al iniciar
   */
  private loadUserFromStorage(): void {
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUserSubject.next(user);
      } catch (error) {
        console.error('Error parsing user from localStorage', error);
        localStorage.removeItem('currentUser');
      }
    }
  }

  /**
   * Registrar un nuevo usuario
   */
  register(userData: UserRegister): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/register`, userData);
  }

/**
 * Iniciar sesión
 */
login(credentials: LoginRequest): Observable<TokenResponse> {
  // FastAPI OAuth2 requiere application/x-www-form-urlencoded
  const body = new URLSearchParams();
  body.set('username', credentials.username);
  body.set('password', credentials.password);

  const headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  };

  return this.http.post<TokenResponse>(`${this.apiUrl}/login`, body.toString(), { headers }).pipe(
    tap(response => {
      // Guardar token en localStorage
      localStorage.setItem('access_token', response.access_token);
      
      // Obtener información del usuario actual
      this.getCurrentUser().subscribe();
    })
  );
}

  /**
   * Obtener información del usuario actual
   */
  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/users/me`).pipe(
      tap(user => {
        // Guardar usuario en el BehaviorSubject y localStorage
        this.currentUserSubject.next(user);
        localStorage.setItem('currentUser', JSON.stringify(user));
      })
    );
  }

  /**
   * Cerrar sesión
   */
  logout(): void {
    // Limpiar localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('currentUser');
    
    // Limpiar usuario actual
    this.currentUserSubject.next(null);
  }

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Obtener el token JWT actual
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Obtener el usuario actual (snapshot)
   */
  getCurrentUserValue(): User | null {
    return this.currentUserSubject.value;
  }
}