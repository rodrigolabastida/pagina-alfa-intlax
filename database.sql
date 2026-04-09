-- Estructura de la Base de Datos para Sistema ALFA 2.0
-- Base de Datos: u653801218_intlaxdata

-- 1. Tabla de Usuarios (Empresa y Clientes)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('empresa', 'cliente') NOT NULL DEFAULT 'cliente',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Reportes (Historial y Autorizaciones)
CREATE TABLE IF NOT EXISTS reportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    mes_periodo VARCHAR(50) NOT NULL, -- Ej: "Marzo 2026"
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('borrador', 'autorizado') DEFAULT 'borrador',
    -- Métricas del reporte extraidas automáticamente al publicarlo
    visualizaciones INT DEFAULT 0,
    espectadores INT DEFAULT 0,
    interacciones INT DEFAULT 0,
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 3. Inserción del Usuario Administrador por Defecto
-- La contraseña por defecto es "Kisesss1."
-- Se genera usando password_hash en PHP. El hash para "Kisesss1." es el siguiente:
INSERT INTO usuarios (nombre, username, password_hash, rol) 
VALUES ('Rodrigo Labs', 'rodrigo_labs', '$2y$10$Wq3k/M9T1tK/lT6.XwK.pOP5E.0R.U1W8sS0WqD.X6q5jB9.M8Y8G', 'empresa');

-- 4. Inserción de un Cliente de Prueba
-- Contraseña por defecto: "cliente123" -> hash: $2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi
INSERT INTO usuarios (nombre, username, password_hash, rol) 
VALUES ('Gobierno Calpulalpan', 'calpulalpan', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'cliente');
