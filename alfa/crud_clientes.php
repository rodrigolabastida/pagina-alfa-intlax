<?php
require_once '../config.php';

// Verificar el acceso
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    die("Acceso no autorizado.");
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $accion = $_POST['accion'] ?? '';
    
    if ($accion === 'guardar') {
        $id = $_POST['cliente_id'] ?? null;
        $nombre = trim($_POST['nombre'] ?? '');
        $username = trim($_POST['username'] ?? '');
        $password = trim($_POST['password'] ?? ''); // Opcional si es edición
        $tipo = $_POST['tipo_organizacion'] ?? 'empresa_privada';
        $dependencia_cargo = trim($_POST['dependencia_cargo'] ?? '');
        $telefono = trim($_POST['telefono'] ?? '');
        $email_contacto = trim($_POST['email_contacto'] ?? '');
        
        try {
            if ($id) {
                // Actualizar (Modificación)
                // Si proporcionó contraseña nueva, se encripta. Si no, se mantiene la actual.
                if (!empty($password)) {
                    $hash = password_hash($password, PASSWORD_DEFAULT);
                    $stmt = $pdo->prepare("UPDATE usuarios SET nombre=?, username=?, password_hash=?, tipo_organizacion=?, dependencia_cargo=?, telefono=?, email_contacto=? WHERE id=? AND rol='cliente'");
                    $stmt->execute([$nombre, $username, $hash, $tipo, $dependencia_cargo, $telefono, $email_contacto, $id]);
                } else {
                    $stmt = $pdo->prepare("UPDATE usuarios SET nombre=?, username=?, tipo_organizacion=?, dependencia_cargo=?, telefono=?, email_contacto=? WHERE id=? AND rol='cliente'");
                    $stmt->execute([$nombre, $username, $tipo, $dependencia_cargo, $telefono, $email_contacto, $id]);
                }
                $msg = "Cliente actualizado correctamente.";
            } else {
                // Crear Nuevo
                if (empty($password)) {
                    throw new Exception("La contraseña es obligatoria para un nuevo usuario.");
                }
                
                // Checar si username ya existe
                $check = $pdo->prepare("SELECT id FROM usuarios WHERE username = ?");
                $check->execute([$username]);
                if ($check->rowCount() > 0) {
                    throw new Exception("El ID de usuario '$username' ya está en uso.");
                }
                
                $hash = password_hash($password, PASSWORD_DEFAULT);
                $stmt = $pdo->prepare("INSERT INTO usuarios (nombre, username, password_hash, rol, tipo_organizacion, dependencia_cargo, telefono, email_contacto) VALUES (?, ?, ?, 'cliente', ?, ?, ?, ?)");
                $stmt->execute([$nombre, $username, $hash, $tipo, $dependencia_cargo, $telefono, $email_contacto]);
                $msg = "Cliente registrado con éxito.";
            }
            
            // Redirigir de vuelta con mensaje de éxito
            header("Location: clientes.php?msg=" . urlencode($msg) . "&type=success");
            exit;
            
        } catch (Exception $e) {
            // Error en base de datos o validación
            header("Location: clientes.php?msg=" . urlencode("Error: " . $e->getMessage()) . "&type=error");
            exit;
        }
    }
}

// Retorno en caso de error o acceso erróneo
header("Location: clientes.php");
exit;
?>
