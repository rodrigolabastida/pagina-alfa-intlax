<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
require_once 'config.php';

echo "<h2>Forzador de Base de Datos - ALFA</h2>";

try {
    // Check if the table exists
    $stmt = $pdo->query("SHOW TABLES LIKE 'usuarios'");
    if($stmt->rowCount() == 0) {
        die("Error crítico: No existe la tabla usuarios en la BD.");
    }

    echo "<p>Tabla 'usuarios' verificada.</p>";
    
    // First, let's describe what's inside
    $stmt = $pdo->query("DESCRIBE usuarios");
    $columns = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    $existing = [];
    foreach($columns as $c) {
        $existing[] = strtolower($c['Field']);
    }
    
    echo "<p>Columnas actuales: " . implode(", ", $existing) . "</p>";

    $camposRequeridos = [
        'tipo_organizacion' => "VARCHAR(50) DEFAULT 'empresa_privada'",
        'dependencia_cargo' => "VARCHAR(150) DEFAULT NULL",
        'telefono' => "VARCHAR(50) DEFAULT NULL",
        'email_contacto' => "VARCHAR(150) DEFAULT NULL"
    ];

    foreach ($camposRequeridos as $campo => $def) {
        if (!in_array(strtolower($campo), $existing)) {
            echo "<li>Falta la columna <b>$campo</b>. Intentando crearla...</li>";
            $pdo->exec("ALTER TABLE usuarios ADD COLUMN $campo $def");
            echo "<li style='color:green;'>-> Columna <b>$campo</b> añadida con éxito.</li>";
        } else {
            echo "<li style='color:blue;'>Columna <b>$campo</b> ya existe. Se omite.</li>";
        }
    }
    
    echo "<br><br><h3 style='color:green;'>PROCESO COMPLETADO. Por favor vuelve al panel de Clientes.</h3>";

} catch (PDOException $e) {
    echo "<h3 style='color:red;'>ERROR PDO: " . $e->getMessage() . "</h3>";
}
?>
