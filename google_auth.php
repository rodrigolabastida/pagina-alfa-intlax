<?php
require_once 'config.php';

// Obtener el token de Google enviado por POST
$id_token = $_POST['credential'] ?? null;

if (!$id_token) {
    die("Token no proporcionado.");
}

// Verificar el token con Google
// En producción, es mejor usar la librería de Google, pero esto es una alternativa rápida para servidores sin composer.
$url = "https://oauth2.googleapis.com/tokeninfo?id_token=" . $id_token;
$response = @file_get_contents($url);

if (!$response) {
    die("Error al verificar el token con Google.");
}

$payload = json_decode($response, true);

if (!isset($payload['sub'])) {
    die("Token inválido.");
}

$google_id = $payload['sub'];
$email = $payload['email'];
$name = $payload['name'];

// Buscar usuario en la base de datos
// 1. Por google_id
$stmt = $pdo->prepare("SELECT id, nombre, rol FROM usuarios WHERE google_id = ? LIMIT 1");
$stmt->execute([$google_id]);
$user = $stmt->fetch();

if (!$user) {
    // 2. Por email (si es la primera vez que inicia sesión con Google)
    $stmt = $pdo->prepare("SELECT id, nombre, rol FROM usuarios WHERE email = ? LIMIT 1");
    $stmt->execute([$email]);
    $user = $stmt->fetch();
    
    if ($user) {
        // Vincular cuenta de Google
        $update = $pdo->prepare("UPDATE usuarios SET google_id = ? WHERE id = ?");
        $update->execute([$google_id, $user['id']]);
    }
}

if ($user) {
    // Iniciar sesión
    $_SESSION['usuario_id'] = $user['id'];
    $_SESSION['nombre'] = $user['nombre'];
    $_SESSION['rol'] = $user['rol'];

    // Redirigir según el rol
    if ($user['rol'] === 'empresa') {
        header("Location: alfa/dashboard.php");
    } else {
        header("Location: cliente/dashboard.php");
    }
    exit;
} else {
    // Usuario no registrado en el sistema
    // Podrías crear el usuario automáticamente si quisieras, 
    // pero para un sistema privado como Bóveda, es mejor denegar el acceso.
    session_destroy();
    header("Location: login.php?error=no_registrado");
    exit;
}
?>
