import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { User, UserRegister, LoginRequest, TokenResponse } from '../models';

/**
 * Servicio de autenticación principal
 * Controla el login, registro, tokens y estado global del usuario
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;
  private userUrl = `${environment.apiUrl}/users`;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadUserFromStorage();
  }

  /** 🔹 Cargar usuario guardado al iniciar la app */
  private loadUserFromStorage(): void {
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUserSubject.next(user);
      } catch (error) {
        console.error('Error cargando usuario desde localStorage:', error);
        localStorage.removeItem('currentUser');
      }
    }
  }

  /** 🔹 Registrar nuevo usuario (envía JSON al backend FastAPI) */
  register(userData: UserRegister): Observable<User> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post<User>(`${this.apiUrl}/register`, userData, { headers });
  }

  /** 🔹 Iniciar sesión y guardar token */
  login(credentials: LoginRequest): Observable<TokenResponse> {
    const body = new URLSearchParams();
    body.set('username', credentials.username);
    body.set('password', credentials.password);

    const headers = { 'Content-Type': 'application/x-www-form-urlencoded' };

    return this.http.post<TokenResponse>(`${this.apiUrl}/login`, body.toString(), { headers }).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        this.getCurrentUser().subscribe();
      })
    );
  }

  /** 🔹 Obtener usuario actual */
  getCurrentUser(): Observable<User> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${this.getToken()}`
    });

    return this.http.get<User>(`${this.userUrl}/me`, { headers }).pipe(
      tap(user => {
        this.currentUserSubject.next(user);
        localStorage.setItem('currentUser', JSON.stringify(user));
      })
    );
  }

  /** 🔹 Actualizar datos del perfil */
  updateProfile(profileData: Partial<User>): Observable<User> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.getToken()}`
    });

    return this.http.put<User>(`${this.userUrl}/update`, profileData, { headers }).pipe(
      tap(updatedUser => {
        localStorage.setItem('currentUser', JSON.stringify(updatedUser));
        this.currentUserSubject.next(updatedUser);
      })
    );
  }

  /** 🔹 Subir foto de perfil */
  uploadProfilePicture(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);

    const headers = new HttpHeaders({
      Authorization: `Bearer ${this.getToken()}`
    });

    return this.http.post(`${this.userUrl}/upload-profile-picture`, formData, { headers }).pipe(
      tap((response: any) => {
        if (response?.profile_picture_url) {
          const updatedUser = {
            ...this.currentUserSubject.value!,
            profile_picture_url: response.profile_picture_url
          };
          localStorage.setItem('currentUser', JSON.stringify(updatedUser));
          this.currentUserSubject.next(updatedUser);
        }
      })
    );
  }

  /** 🔹 Eliminar foto de perfil */
  deleteProfilePicture(): Observable<any> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${this.getToken()}`
    });

    return this.http.delete(`${this.userUrl}/delete-profile-picture`, { headers }).pipe(
      tap(() => {
        const updatedUser = {
          ...this.currentUserSubject.value!,
          profile_picture_url: null
        };
        localStorage.setItem('currentUser', JSON.stringify(updatedUser));
        this.currentUserSubject.next(updatedUser);
      })
    );
  }

  /** 🔹 Cambiar contraseña */
  changePassword(newPassword: string): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.getToken()}`
    });

    return this.http.put(`${this.userUrl}/change-password`, { password: newPassword }, { headers });
  }

  /** 🔹 Cerrar sesión */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  /** 🔹 Verificar si el usuario está autenticado */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /** 🔹 Obtener token JWT actual */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /** 🔹 Obtener el usuario actual (snapshot) */
  getCurrentUserValue(): User | null {
    return this.currentUserSubject.value;
  }
}
