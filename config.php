<?php
$host = "localhost";
$dbname = "u653801218_intlaxdata";
$username = "u653801218_Alfaintlax";
$password = "Rodrigoin9.";

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    // Configurar PDO para reportar excepciones en caso de error
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // Obtener resultados como arrays asociativos por defecto
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Error de conexión a la base de datos: " . $e->getMessage());
}

// Iniciar sesión de manera global si no está iniciada ya
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}
?>
