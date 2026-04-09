<?php
require_once 'config.php';

echo "<h2>Actualizador de Base de Datos ALFA</h2>";

$campos = [
    'tipo_organizacion' => "VARCHAR(50) DEFAULT 'empresa_privada'",
    'dependencia_cargo' => "VARCHAR(150) DEFAULT NULL",
    'email_contacto' => "VARCHAR(150) DEFAULT NULL",
    'telefono' => "VARCHAR(50) DEFAULT NULL"
];

foreach ($campos as $columna => $definicion) {
    try {
        // Ejecutar alter table. Si ya existe, lanzará excepción PDOException
        $pdo->exec("ALTER TABLE usuarios ADD COLUMN $columna $definicion");
        echo "<p style='color:green;'>Columna <b>$columna</b> añadida correctamente.</p>";
    } catch (PDOException $e) {
        // El código de error 1060 significa "Duplicate column name" (La columna ya existe)
        if ($e->errorInfo[1] == 1060) {
            echo "<p style='color:gray;'>La columna <b>$columna</b> ya existe. Omitiendo.</p>";
        } else {
            echo "<p style='color:red;'>Error al añadir <b>$columna</b>: " . $e->getMessage() . "</p>";
        }
    }
}

// Asegurarse de que el usuario administrador tenga el email actualizado en su propio campo si fuese necesario
$pdo->exec("UPDATE usuarios SET email_contacto = 'contacto@intlax.claud', dependencia_cargo = 'Intlax Administrador' WHERE username = 'rodrigo_labs'");

echo "<br><h3><a href='login.php'>Volver al Login o ALFA</a></h3>";
?>
