import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { User } from '../../../models';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
  currentUser: User | null = null;
  profileForm!: FormGroup;
  passwordForm!: FormGroup;
  
  loading = false;
  profilePictureUrl: string | null = null;
  selectedFile: File | null = null;
  previewUrl: string | null = null;
  
  // Pestañas
  activeTab: 'profile' | 'security' = 'profile';

  constructor(
    private authService: AuthService,
    private formBuilder: FormBuilder,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Obtener usuario actual
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (user) {
        this.loadProfilePicture();
        this.initForms();
      }
    });
  }

  /**
   * Inicializar formularios
   */
  initForms(): void {
    // Formulario de perfil
    this.profileForm = this.formBuilder.group({
      full_name: [this.currentUser?.full_name || ''],
      email: [this.currentUser?.email || '', [Validators.required, Validators.email]],
      phone: [this.currentUser?.phone || ''],
      bio: [this.currentUser?.bio || '']
    });

    // Formulario de contraseña
    this.passwordForm = this.formBuilder.group({
      current_password: ['', Validators.required],
      new_password: ['', [Validators.required, Validators.minLength(6)]],
      confirm_password: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  /**
   * Validador de coincidencia de contraseñas
   */
  passwordMatchValidator(g: FormGroup) {
    return g.get('new_password')?.value === g.get('confirm_password')?.value
      ? null : { mismatch: true };
  }

  /**
   * Cambiar de pestaña
   */
  switchTab(tab: 'profile' | 'security'): void {
    this.activeTab = tab;
  }

  /**
   * Cargar foto de perfil
   */
  loadProfilePicture(): void {
    if (this.currentUser?.profile_picture) {
      const token = localStorage.getItem('access_token');
      const filename = this.currentUser.profile_picture.split('/').pop();
      this.profilePictureUrl = `http://localhost:8001/users/me/profile-picture/${filename}?token=${token}`;
    }
  }

  /**
   * Seleccionar archivo de imagen
   */
  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Validar tipo
      if (!file.type.startsWith('image/')) {
        alert('❌ Por favor selecciona una imagen válida');
        return;
      }

      // Validar tamaño (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('❌ La imagen no debe superar 5MB');
        return;
      }

      this.selectedFile = file;

      // Crear preview
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.previewUrl = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  /**
   * Subir foto de perfil
   */
  uploadProfilePicture(): void {
    if (!this.selectedFile) {
      alert('❌ Por favor selecciona una imagen');
      return;
    }

    this.loading = true;

    this.authService.uploadProfilePicture(this.selectedFile).subscribe({
      next: (response: any) => {
        alert('✅ Foto de perfil actualizada');
        this.profilePictureUrl = this.previewUrl;
        this.selectedFile = null;
        this.loading = false;
        
        // Recargar datos del usuario
        this.authService.getCurrentUser().subscribe();
      },
      error: (error: any) => {
        console.error('Error uploading picture:', error);
        alert('❌ Error al subir la foto: ' + (error.error?.detail || 'Error desconocido'));
        this.loading = false;
      }
    });
  }

  /**
   * Cancelar selección de foto
   */
  cancelImageSelection(): void {
    this.selectedFile = null;
    this.previewUrl = null;
  }

  /**
   * Eliminar foto de perfil
   */
  deleteProfilePicture(): void {
    if (!confirm('¿Estás seguro de eliminar tu foto de perfil?')) {
      return;
    }

    this.loading = true;

    this.authService.deleteProfilePicture().subscribe({
      next: () => {
        alert('✅ Foto de perfil eliminada');
        this.profilePictureUrl = null;
        this.previewUrl = null;
        this.loading = false;
        
        // Recargar datos del usuario
        this.authService.getCurrentUser().subscribe();
      },
      error: (error: any) => {
        console.error('Error deleting picture:', error);
        alert('❌ Error al eliminar la foto');
        this.loading = false;
      }
    });
  }

  /**
   * Guardar cambios de perfil
   */
  saveProfile(): void {
    if (this.profileForm.invalid) {
      alert('❌ Por favor completa correctamente el formulario');
      return;
    }

    this.loading = true;
    const profileData = this.profileForm.value;

    this.authService.updateProfile(profileData).subscribe({
      next: () => {
        alert('✅ Perfil actualizado correctamente');
        this.loading = false;
        
        // Recargar datos del usuario
        this.authService.getCurrentUser().subscribe();
      },
      error: (error: any) => {
        console.error('Error updating profile:', error);
        alert('❌ Error al actualizar perfil: ' + (error.error?.detail || 'Error desconocido'));
        this.loading = false;
      }
    });
  }

  /**
   * Cambiar contraseña
   */
  changePassword(): void {
    if (this.passwordForm.invalid) {
      alert('❌ Por favor completa correctamente el formulario');
      return;
    }

    if (this.passwordForm.errors?.['mismatch']) {
      alert('❌ Las contraseñas no coinciden');
      return;
    }

    this.loading = true;
    const { new_password } = this.passwordForm.value;

    this.authService.changePassword(new_password).subscribe({
  next: () => {
    alert('✅ Contraseña actualizada correctamente');
    this.passwordForm.reset();
    this.loading = false;
  },
  error: (error: any) => {
    console.error('Error changing password:', error);
    alert('❌ Error al cambiar contraseña: ' + (error.error?.detail || 'Error desconocido'));
    this.loading = false;
  }
});

  }

  /**
   * Volver al dashboard
   */
  goBack(): void {
    this.router.navigate(['/dashboard']);

  }

  get userInitial(): string {
  return this.currentUser?.username
    ? this.currentUser.username.charAt(0).toUpperCase()
    : '?';
}

}