import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../../services';


/**
 * Componente de inicio de sesión
 */
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  loading = false;
  submitted = false;
  errorMessage = '';
  returnUrl = '/dashboard';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Crear el formulario con validaciones
    this.loginForm = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });

    // Obtener la URL de retorno si existe
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
  }

  // Getter para acceder fácilmente a los campos del formulario
  get f() {
    return this.loginForm.controls;
  }

  /**
   * Manejar el envío del formulario
   */
  onSubmit(): void {
    this.submitted = true;
    this.errorMessage = '';

    // Validar el formulario
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;

    // Llamar al servicio de autenticación
    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        // Login exitoso, redirigir al dashboard
        this.router.navigate([this.returnUrl]);
      },
      error: (error) => {
      // Mostrar error
      console.error('Login error:', error);
      
      if (error.error?.detail) {
        // Si detail es un string
        if (typeof error.error.detail === 'string') {
          this.errorMessage = error.error.detail;
        } 
        // Si detail es un array (validación de FastAPI)
        else if (Array.isArray(error.error.detail)) {
          this.errorMessage = error.error.detail.map((e: any) => e.msg).join(', ');
        }
        // Si no, mensaje genérico
        else {
          this.errorMessage = 'Error al iniciar sesión. Verifica tus credenciales.';
        }
      } else {
        this.errorMessage = 'Error al iniciar sesión. Verifica tus credenciales.';
      }
      
      this.loading = false;
    }
    });
  }
}
