<?php
require_once '../config.php';

if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    die(json_encode(['success' => false, 'message' => 'No autorizado']));
}

$cliente_id = $_POST['cliente_id'] ?? 0;
if (!$cliente_id) {
    die(json_encode(['success' => false, 'message' => 'Cliente inválido']));
}

$folder_name = 'client_' . $cliente_id;
$ruta_carpeta = __DIR__ . '/../Archivo_Medios/Testigos/' . $folder_name;

if (!file_exists($ruta_carpeta)) {
    mkdir($ruta_carpeta, 0755, true);
}

// Lógica de borrado
if (isset($_POST['borrar_archivo'])) {
    $archivo = basename($_POST['borrar_archivo']); // basename por seguridad
    $ruta_archivo = $ruta_carpeta . '/' . $archivo;
    
    if (file_exists($ruta_archivo)) {
        unlink($ruta_archivo);
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['success' => false, 'message' => 'Archivo no encontrado']);
    }
    exit;
}

// Lógica de subida múltiple
if (!empty($_FILES['evidencia'])) {
    $archivos = $_FILES['evidencia'];
    $errores = [];
    
    foreach ($archivos['tmp_name'] as $index => $tmp_name) {
        $nombre_original = basename($archivos['name'][$index]);
        $ext = strtolower(pathinfo($nombre_original, PATHINFO_EXTENSION));
        
        // Validación de tipo
        if (!in_array($ext, ['jpg', 'jpeg', 'png'])) {
            $errores[] = "Extension no permitida: $nombre_original";
            continue;
        }
        
        $ruta_destino = $ruta_carpeta . '/' . $nombre_original;
        
        if (!move_uploaded_file($tmp_name, $ruta_destino)) {
            $errores[] = "Error moviendo: $nombre_original";
        }
    }
    
    if (count($errores) > 0) {
        echo json_encode(['success' => false, 'message' => implode(", ", $errores)]);
    } else {
        echo json_encode(['success' => true]);
    }
    exit;
}

echo json_encode(['success' => false, 'message' => 'Ninguna acción realizada.']);
?>
