<?php
require_once 'config.php';

echo "<h2>Actualizador de Base de Datos - Google OAuth v3.0</h2>";

$campos = [
    'email' => "VARCHAR(255) UNIQUE AFTER username",
    'google_id' => "VARCHAR(255) UNIQUE AFTER email"
];

foreach ($campos as $columna => $definicion) {
    try {
        $pdo->exec("ALTER TABLE usuarios ADD COLUMN $columna $definicion");
        echo "<p style='color:green;'>Columna <b>$columna</b> añadida correctamente.</p>";
    } catch (PDOException $e) {
        if ($e->errorInfo[1] == 1060) {
            echo "<p style='color:gray;'>La columna <b>$columna</b> ya existe. Omitiendo.</p>";
        } else {
            echo "<p style='color:red;'>Error al añadir <b>$columna</b>: " . $e->getMessage() . "</p>";
        }
    }
}

// Opcional: Migrar email_contacto a email si existe y no está vacío
try {
    $pdo->exec("UPDATE usuarios SET email = email_contacto WHERE email IS NULL AND email_contacto IS NOT NULL");
    echo "<p style='color:blue;'>Migración de emails completada.</p>";
} catch (PDOException $e) {
    echo "<p style='color:orange;'>Aviso: No se pudo migrar emails: " . $e->getMessage() . "</p>";
}

echo "<br><h3><a href='login.php'>Volver al Login</a></h3>";
?>
