import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../../services';

/**
 * Componente de registro de nuevos usuarios
 */
@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  loading = false;
  submitted = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Crear el formulario con validaciones
    this.registerForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      full_name: [''],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  // Getter para acceder fácilmente a los campos del formulario
  get f() {
    return this.registerForm.controls;
  }

  /**
   * Manejar el envío del formulario
   */
  onSubmit(): void {
    this.submitted = true;
    this.errorMessage = '';
    this.successMessage = '';

    // Validar el formulario
    if (this.registerForm.invalid) {
      return;
    }

    this.loading = true;

    // Llamar al servicio de registro
    this.authService.register(this.registerForm.value).subscribe({
      next: () => {
        // Registro exitoso
        this.successMessage = '¡Cuenta creada exitosamente! Redirigiendo al login...';
        
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
      // Mostrar error
      console.error('Register error:', error);
      
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
          this.errorMessage = 'Error al crear la cuenta. Intenta nuevamente.';
        }
      } else {
        this.errorMessage = 'Error al crear la cuenta. Intenta nuevamente.';
      }
      
      this.loading = false;
    }
    });
  }
}
