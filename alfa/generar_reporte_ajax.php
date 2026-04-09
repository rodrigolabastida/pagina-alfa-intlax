<?php
require_once '../config.php';

header('Content-Type: application/json');

if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    die(json_encode(['status' => 'error', 'log' => 'No autorizado']));
}

$cliente_id = $_POST['cliente_id'] ?? 0;
$periodo = trim($_POST['periodo'] ?? '');
$lugar = trim($_POST['lugar'] ?? '');

if (!$cliente_id || empty($periodo)) {
    die(json_encode(['status' => 'error', 'log' => 'Datos insuficientes.']));
}

try {
    // Obtener nombre del cliente
    $stmt = $pdo->prepare("SELECT nombre FROM usuarios WHERE id = ?");
    $stmt->execute([$cliente_id]);
    $cliente_nombre = $stmt->fetchColumn();

    if (!$cliente_nombre) {
        throw new Exception("Cliente no encontrado en BD.");
    }

    $folder = 'client_' . $cliente_id;
    $pythonScript = realpath(__DIR__ . '/../Archivo_Medios/generador_reportes.py');
    
    if (!$pythonScript) {
        throw new Exception("Script generador_reportes.py no encontrado.");
    }
    
    // Comando para Python enviando argumentos dinámicos
    $cmd = "python3 " . escapeshellarg($pythonScript) . 
           " --folder " . escapeshellarg($folder) . 
           " --cliente " . escapeshellarg($cliente_nombre) . 
           " --periodo " . escapeshellarg($periodo) . 
           " --lugar " . escapeshellarg($lugar) . " 2>&1";
           
    $output = shell_exec($cmd);
    
    // --- ACTUALIZAR LA BASE DE DATOS TRAS LA GENERACIÓN ---
    $reportesDir = realpath(__DIR__ . '/../reportes');
    if ($reportesDir) {
        // Buscar el archivo generado. El nombre en Python es f"Reporte_{folder_name.replace(' ', '_')}_{periodo_uso.replace(' ', '_')}.html"
        $safe_folder = str_replace(' ', '_', $folder);
        $safe_periodo = str_replace(' ', '_', $periodo);
        $filename = "Reporte_{$safe_folder}_{$safe_periodo}.html";
        
        $ruta_reporte = $reportesDir . '/' . $filename;
        
        if (file_exists($ruta_reporte)) {
            // Revisar si ya está en la DB
            $stmtCheck = $pdo->prepare("SELECT id FROM reportes WHERE nombre_archivo = ?");
            $stmtCheck->execute([$filename]);
            
            if ($stmtCheck->rowCount() == 0) {
                // Registrarlo nuevo en borrador
                $stmtInsert = $pdo->prepare("INSERT INTO reportes (cliente_id, nombre_archivo, mes_periodo, estado, visualizaciones, espectadores, interacciones) VALUES (?, ?, ?, 'borrador', 0, 0, 0)");
                $stmtInsert->execute([$cliente_id, $filename, $periodo]);
                $output .= "\n[PHP] -> Indexación en MySQL correcta: " . $filename;
            } else {
                // Ya existe, actualizar el periodo
                $stmtUpdate = $pdo->prepare("UPDATE reportes SET mes_periodo = ? WHERE nombre_archivo = ?");
                $stmtUpdate->execute([$periodo, $filename]);
                $output .= "\n[PHP] -> Actualización en MySQL correcta.";
            }
        } else {
            $output .= "\n[PHP ADVERTENCIA] -> Python procesó, pero el archivo $filename no apareció en /reportes.";
        }
    }
    
    echo json_encode([
        "status" => "success", 
        "log" => $output
    ]);

} catch (Exception $e) {
    echo json_encode([
        "status" => "error", 
        "log" => "Error interno: " . $e->getMessage()
    ]);
}
?>
