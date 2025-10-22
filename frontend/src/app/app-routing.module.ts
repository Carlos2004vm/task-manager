import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard, NoAuthGuard } from './guards';

const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  
  // Rutas de autenticación
  {
    path: 'login',
    canActivate: [NoAuthGuard],
    loadChildren: () => import('./modules/auth/auth.module').then(m => m.AuthModule)  // ← CAMBIÓ
  },
  
  // Rutas protegidas
  {
    path: 'dashboard',
    canActivate: [AuthGuard],
    loadChildren: () => import('./modules/dashboard/dashboard.module').then(m => m.DashboardModule)  // ← CAMBIÓ
  },
  
  // Ruta 404
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