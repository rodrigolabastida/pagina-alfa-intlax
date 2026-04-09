<?php
require_once '../config.php';

// Verificar que sea admin
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    http_response_code(403);
    echo json_encode(["status" => "error", "message" => "No autorizado."]);
    exit;
}

header('Content-Type: application/json');

try {
    // Ruta absoluta al script de Python
    $pythonScript = realpath(__DIR__ . '/../Archivo_Medios/generador_reportes.py');
    
    if (!$pythonScript || !file_exists($pythonScript)) {
        throw new Exception("El script de Python no se encontró.");
    }
    
    // Comando para ejecutar el script.
    $command = "python3 " . escapeshellarg($pythonScript) . " 2>&1";
    $output = shell_exec($command);
    
    // --- ACTUALIZAR LA BASE DE DATOS TRAS LA GENERACIÓN ---
    // Escaneamos la carpeta reportes e insertamos en DB si no existen
    $reportesDir = realpath(__DIR__ . '/../reportes');
    if ($reportesDir) {
        $archivos = glob($reportesDir . '/*.html');
        
        // Obtener clientes para asociarlos
        $stmtClientes = $pdo->query("SELECT id, nombre FROM usuarios WHERE rol = 'cliente'");
        $clientes = $stmtClientes->fetchAll();
        
        foreach ($archivos as $archivo) {
            $filename = basename($archivo);
            
            // Si el archivo ya está en la BD, no hacemos nada
            $stmtCheck = $pdo->prepare("SELECT id FROM reportes WHERE nombre_archivo = ?");
            $stmtCheck->execute([$filename]);
            if ($stmtCheck->rowCount() == 0) {
                // Intentar deducir cliente y mes del nombre: Ej: Reporte_Calpulalpan_Marzo_2026.html
                $cliente_id_asociado = null;
                $mes_detectado = 'Mes Actual'; // default
                
                foreach ($clientes as $c) {
                    // Criterio muy simple: si el nombre del archivo contiene parte del nombre del cliente
                    // (En la realidad quiza requiera mapeo más exacto, p.ej. "Calpulalpan" en nombre_archivo)
                    $palabra_clave = explode(" ", $c['nombre'])[0]; 
                    if (stripos($filename, $palabra_clave) !== false || $c['nombre'] == 'Gobierno Calpulalpan') {
                        $cliente_id_asociado = $c['id'];
                        break;
                    }
                }
                
                // Si encontramos un cliente asociado (para desarrollo, cliente_id = 2 es Calpulalpan)
                if (!$cliente_id_asociado) { $cliente_id_asociado = 2; } 
                
                // Insertar en la BD en estado 'borrador'
                $stmtInsert = $pdo->prepare("INSERT INTO reportes (cliente_id, nombre_archivo, mes_periodo, estado, visualizaciones, espectadores, interacciones) VALUES (?, ?, ?, 'borrador', 0, 0, 0)");
                // Parseamos visualizaciones (ej. si leyéramos el html). Por ahora 0, en la v3 python lo inyecta directo.
                $stmtInsert->execute([$cliente_id_asociado, $filename, 'Reciente (Autogenerado)']);
            }
        }
    }
    
    echo json_encode([
        "status" => "success", 
        "message" => "Script ejecutado correctamente y DB sincronizada.",
        "log" => $output
    ]);
} catch (Exception $e) {
    echo json_encode([
        "status" => "error", 
        "message" => "Error interno: " . $e->getMessage()
    ]);
}
?>
