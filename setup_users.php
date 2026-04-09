<?php
require_once 'config.php';

echo "<h2>Verificador y Setup de Usuarios ALFA</h2>";

try {
    // Verificar si la tabla existe
    $stmt = $pdo->query("SHOW TABLES LIKE 'usuarios'");
    if ($stmt->rowCount() == 0) {
        die("Error: La tabla 'usuarios' no existe. Asegúrate de ejecutar database.sql en phpMyAdmin.");
    }
    
    // Crear o actualizar el usuario administrador maestro
    $username = 'rodrigo_labs';
    $password = 'Kisesss1.';
    $hash = password_hash($password, PASSWORD_DEFAULT);
    
    // Revisar si existe
    $stmt = $pdo->prepare("SELECT id FROM usuarios WHERE username = ?");
    $stmt->execute([$username]);
    
    if ($stmt->rowCount() > 0) {
        // Actualizar
        $stmtUpdate = $pdo->prepare("UPDATE usuarios SET password_hash = ? WHERE username = ?");
        $stmtUpdate->execute([$hash, $username]);
        echo "<p style='color:green;'>Usuario 'rodrigo_labs' ACTUALIZADO con un nuevo Hash seguro nativo del servidor.</p>";
    } else {
        // Insertar
        $stmtInsert = $pdo->prepare("INSERT INTO usuarios (nombre, username, password_hash, rol) VALUES ('Rodrigo Labs', ?, ?, 'empresa')");
        $stmtInsert->execute([$username, $hash]);
        echo "<p style='color:green;'>Usuario 'rodrigo_labs' CREADO con éxito.</p>";
    }
    
    // Crear o actualizar el usuario cliente de prueba
    $clienteUser = 'calpulalpan';
    $clientePass = 'cliente123';
    $clienteHash = password_hash($clientePass, PASSWORD_DEFAULT);
    
    $stmt = $pdo->prepare("SELECT id FROM usuarios WHERE username = ?");
    $stmt->execute([$clienteUser]);
    
    if ($stmt->rowCount() > 0) {
        $stmtUpdate = $pdo->prepare("UPDATE usuarios SET password_hash = ? WHERE username = ?");
        $stmtUpdate->execute([$clienteHash, $clienteUser]);
        echo "<p style='color:green;'>Usuario cliente 'calpulalpan' ACTUALIZADO.</p>";
    } else {
        $stmtInsert = $pdo->prepare("INSERT INTO usuarios (nombre, username, password_hash, rol) VALUES ('Gobierno Calpulalpan', ?, ?, 'cliente')");
        $stmtInsert->execute([$clienteUser, $clienteHash]);
        echo "<p style='color:green;'>Usuario cliente 'calpulalpan' CREADO.</p>";
    }
    
    echo "<br><br><h3><a href='login.php'>Haz clic aquí para ir al Login</a></h3>";
    echo "<p>Nota de seguridad: Puedes eliminar este archivo (setup_users.php) de tu servidor cuando hayas comprobado que funciona.</p>";

} catch (Exception $e) {
    echo "<p style='color:red;'>Error de Base de Datos: " . $e->getMessage() . "</p>";
}
