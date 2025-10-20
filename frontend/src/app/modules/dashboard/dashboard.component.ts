import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, TaskService } from '../../services';
import { User, Task, TaskStats, TaskCreate, TaskUpdate } from '../../models';

/**
 * Componente principal del dashboard
 */
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;
  tasks: Task[] = [];
  stats: TaskStats | null = null;
  currentFilter: 'all' | 'pending' | 'completed' = 'all';
  
  // Modal de tarea
  showTaskModal = false;
  taskForm!: FormGroup;
  editingTask: Task | null = null;
  loading = false;

  constructor(
    private authService: AuthService,
    private taskService: TaskService,
    private formBuilder: FormBuilder,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Obtener usuario actual
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    // Crear formulario de tarea
    this.taskForm = this.formBuilder.group({
      title: ['', Validators.required],
      description: [''],
      priority: ['medium'],
      due_date: ['']
    });

    // Cargar datos iniciales
    this.loadTasks();
    this.loadStats();
  }

  /**
   * Cargar tareas según filtro actual
   */
  loadTasks(): void {
    const filters: any = {};
    
    if (this.currentFilter === 'pending') {
      filters.is_completed = false;
    } else if (this.currentFilter === 'completed') {
      filters.is_completed = true;
    }

    this.taskService.getTasks(filters).subscribe({
      next: (tasks) => {
        this.tasks = tasks;
      },
      error: (error) => {
        console.error('Error loading tasks:', error);
      }
    });
  }

  /**
   * Cargar estadísticas
   */
  loadStats(): void {
    this.taskService.getStats().subscribe({
      next: (stats) => {
        this.stats = stats;
      },
      error: (error) => {
        console.error('Error loading stats:', error);
      }
    });
  }

  /**
   * Filtrar tareas
   */
  filterTasks(filter: 'all' | 'pending' | 'completed'): void {
    this.currentFilter = filter;
    this.loadTasks();
  }

  /**
   * Cambiar estado de completado de una tarea
   */
  toggleTaskComplete(task: Task): void {
    if (task.is_completed) {
      this.taskService.incompleteTask(task.id).subscribe({
        next: () => {
          this.loadTasks();
          this.loadStats();
        }
      });
    } else {
      this.taskService.completeTask(task.id).subscribe({
        next: () => {
          this.loadTasks();
          this.loadStats();
        }
      });
    }
  }

  /**
   * Abrir modal para crear tarea
   */
  openTaskModal(): void {
    this.editingTask = null;
    this.taskForm.reset({ priority: 'medium' });
    this.showTaskModal = true;
  }

  /**
   * Abrir modal para editar tarea
   */
  editTask(task: Task): void {
    this.editingTask = task;
    this.taskForm.patchValue({
      title: task.title,
      description: task.description,
      priority: task.priority,
      due_date: task.due_date
    });
    this.showTaskModal = true;
  }

  /**
   * Cerrar modal
   */
  closeTaskModal(): void {
    this.showTaskModal = false;
    this.editingTask = null;
    this.taskForm.reset();
  }

  /**
   * Guardar tarea (crear o actualizar)
   */
  saveTask(): void {
    if (this.taskForm.invalid) {
      return;
    }

    this.loading = true;
    const taskData = this.taskForm.value;

    if (this.editingTask) {
      // Actualizar tarea existente
      this.taskService.updateTask(this.editingTask.id, taskData).subscribe({
        next: () => {
          this.loadTasks();
          this.loadStats();
          this.closeTaskModal();
          this.loading = false;
        },
        error: (error) => {
          console.error('Error updating task:', error);
          this.loading = false;
        }
      });
    } else {
      // Crear nueva tarea
      this.taskService.createTask(taskData).subscribe({
        next: () => {
          this.loadTasks();
          this.loadStats();
          this.closeTaskModal();
          this.loading = false;
        },
        error: (error) => {
          console.error('Error creating task:', error);
          this.loading = false;
        }
      });
    }
  }

  /**
   * Eliminar tarea
   */
  deleteTask(task: Task): void {
    if (confirm(`¿Estás seguro de eliminar la tarea "${task.title}"?`)) {
      this.taskService.deleteTask(task.id).subscribe({
        next: () => {
          this.loadTasks();
          this.loadStats();
        },
        error: (error) => {
          console.error('Error deleting task:', error);
        }
      });
    }
  }

  /**
   * Cerrar sesión
   */
  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}