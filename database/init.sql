-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS taskmanager;
USE taskmanager;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6',
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de tareas
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    due_date DATE,
    user_id INT NOT NULL,
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_category_id ON tasks(category_id);
CREATE INDEX idx_tasks_is_completed ON tasks(is_completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Insertar usuario de prueba
-- Usuario: admin
-- Password: admin123
-- Hash generado con bcrypt 4.0.1
INSERT INTO users (username, email, hashed_password, full_name) VALUES
('admin', 'admin@taskmanager.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Administrador');

-- Insertar categorías de ejemplo
INSERT INTO categories (name, color, user_id) VALUES
('Trabajo', '#3B82F6', 1),
('Personal', '#10B981', 1),
('Urgente', '#EF4444', 1),
('Ideas', '#F59E0B', 1);

-- Insertar tareas de ejemplo
INSERT INTO tasks (title, description, priority, due_date, user_id, category_id, is_completed) VALUES
('Bienvenido al Task Manager', 'Esta es tu primera tarea de ejemplo. Puedes editarla o eliminarla.', 'medium', DATE_ADD(CURDATE(), INTERVAL 7 DAY), 1, 1, FALSE),
('Explorar las categorías', 'Prueba crear nuevas categorías para organizar tus tareas', 'low', DATE_ADD(CURDATE(), INTERVAL 3 DAY), 1, 2, FALSE),
('Tarea completada de ejemplo', 'Esta tarea ya está marcada como completada', 'high', CURDATE(), 1, 3, TRUE);