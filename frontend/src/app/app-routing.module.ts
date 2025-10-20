import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard, NoAuthGuard } from './guards';

/**
 * Configuración de rutas de la aplicación
 */
const routes: Routes = [
  // Ruta por defecto - redirigir a dashboard
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  
  // Rutas de autenticación (sin protección, solo usuarios NO autenticados)
  {
    path: 'login',
    canActivate: [NoAuthGuard],
    loadChildren: () => import('./components/auth/auth.module').then(m => m.AuthModule)
  },
  
  // Rutas protegidas (requieren autenticación)
  {
    path: 'dashboard',
    canActivate: [AuthGuard],
    loadChildren: () => import('./components/dashboard/dashboard.module').then(m => m.DashboardModule)
  },
  
  // Ruta 404 - Not Found
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }