<?php
require_once '../config.php';

// Verificar el acceso
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    header("Location: ../login.php");
    exit;
}

$cliente_id = $_GET['id'] ?? 0;
if (!$cliente_id) {
    header("Location: clientes.php");
    exit;
}

// Cargar estado del cliente
$stmt = $pdo->prepare("SELECT * FROM usuarios WHERE id = ? AND rol = 'cliente'");
$stmt->execute([$cliente_id]);
$cliente = $stmt->fetch();

if (!$cliente) {
    die("Cliente no encontrado.");
}

$folder_name = 'client_' . $cliente_id;
$ruta_carpeta = __DIR__ . '/../Archivo_Medios/Testigos/' . $folder_name;

// Asegurar que la carpeta existe por si se generó antes del update
if (!file_exists($ruta_carpeta)) {
    mkdir($ruta_carpeta, 0755, true);
}

// Leer imágenes actuales
$archivos = [];
foreach (scandir($ruta_carpeta) as $archivo) {
    if ($archivo !== '.' && $archivo !== '..' && !is_dir($ruta_carpeta . '/' . $archivo)) {
        if (preg_match('/\.(jpg|jpeg|png)$/i', $archivo)) {
            $archivos[] = $archivo;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Reportes - <?= htmlspecialchars($cliente['nombre']) ?></title>
    <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --bg-dark: #0a0a0a;
            --bg-card: #141414;
            --bg-surface: #1a1a1a;
            --primary: #FFD700;
            --text-main: #f5f5f5;
            --text-muted: #888;
            --border-color: #333;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }
        
        .container { max-width: 1000px; margin: 0 auto; width: 100%; padding: 40px 20px; }
        .action-btn { background: none; border: 1px solid var(--border-color); color: var(--text-main); padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; transition: 0.3s; text-decoration: none; }
        .action-btn:hover { border-color: var(--primary); color: var(--primary); }

        .header-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid var(--border-color); padding-bottom: 20px; }
        .page-title { font-size: 1.8rem; font-weight: 300; color: var(--text-muted); }
        .page-title strong { color: #fff; font-weight: 800; }
        .badge { padding: 4px 8px; font-size: 0.7rem; border-radius: 12px; font-weight: 600; text-transform: uppercase; border: 1px solid var(--primary); color: var(--primary); }

        .card { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 30px; margin-bottom: 30px; }
        .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 20px; color: var(--primary); text-transform: uppercase; font-family: 'Anton', sans-serif; letter-spacing: 1px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }

        /* Formulario y Botones */
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; }
        .form-group input { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); background-color: #000; color: #fff; font-size: 0.95rem; }
        .form-group input:focus { outline: none; border-color: var(--primary); }
        
        .btn-submit { display: inline-flex; justify-content: center; align-items: center; gap: 10px; width: 100%; background-color: var(--primary); color: #000; font-weight: 800; padding: 15px; border: none; border-radius: 6px; font-size: 1.1rem; cursor: pointer; text-transform: uppercase; transition: 0.2s; }
        .btn-submit:hover { filter: brightness(1.1); transform: translateY(-2px); }

        /* Subidor de Evidencias */
        .upload-area { border: 2px dashed var(--border-color); border-radius: 12px; padding: 40px; text-align: center; background: rgba(0,0,0,0.2); cursor: pointer; transition: 0.3s; margin-bottom: 20px; }
        .upload-area:hover, .upload-area.dragover { border-color: var(--primary); background: rgba(255, 215, 0, 0.05); }
        .upload-icon { font-size: 3rem; color: var(--text-muted); margin-bottom: 10px; }
        
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; margin-top: 20px; }
        .thumb-box { position: relative; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color); width: 100%; padding-bottom: 100%; background: #000; }
        .thumb-box img { position: absolute; width: 100%; height: 100%; object-fit: cover; }
        .thumb-delete { position: absolute; top: 2px; right: 2px; background: rgba(200,0,0,0.8); color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; font-size: 12px; }

        /* Consola / Terminal */
        #console-container { display: none; background-color: #000; border: 1px solid #333; border-radius: 8px; font-family: monospace; font-size: 0.85rem; height: 250px; flex-direction: column; }
        #console-header { background-color: #111; padding: 8px 15px; border-bottom: 1px solid #333; color: #888; font-weight: bold; border-radius: 8px 8px 0 0; }
        #console-output { padding: 15px; overflow-y: auto; flex-grow: 1; color: #00ff00; white-space: pre-wrap; line-height: 1.4; }
    </style>
</head>
<body>

<div class="container">
    <div class="header-top">
        <h2 class="page-title">Gestión Inmersiva: <strong><?= htmlspecialchars($cliente['nombre']) ?></strong></h2>
        <a href="clientes.php" class="action-btn"><i class="fas fa-arrow-left"></i> Volver</a>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
        
        <!-- Panel 1: Archivos (La Cosecha de Testigos) -->
        <div class="card">
            <h3 class="card-title"><i class="fas fa-camera"></i> 1. Cosecha de Testigos</h3>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px;">
                Arrastra las capturas de Meta Business Suite de este mes. El motor Python leerá cada una automáticamente.
            </p>

            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="fileInput" name="evidencia" accept="image/png, image/jpeg" style="display:none;" multiple>
                <input type="hidden" name="cliente_id" id="cliente_id" value="<?= htmlspecialchars($cliente_id) ?>">
                
                <div class="upload-area" id="dropZone" onclick="document.getElementById('fileInput').click()">
                    <i class="fas fa-cloud-upload-alt upload-icon"></i>
                    <p>Haz clic o arrastra imágenes aquí</p>
                    <small style="color: var(--text-muted); margin-top:5px; display:block;">Permitidos: JPG, PNG</small>
                </div>
            </form>

            <div id="uploadStatus" style="font-size: 0.85rem; text-align: center; color: var(--primary);"></div>

            <div class="gallery" id="imageGallery">
                <?php foreach($archivos as $a): ?>
                <div class="thumb-box" id="thumb_<?= md5($a) ?>">
                    <img src="../Archivo_Medios/Testigos/<?= $folder_name ?>/<?= htmlspecialchars($a) ?>">
                    <button class="thumb-delete" onclick="borrarEvidencia('<?= htmlspecialchars($a) ?>', '<?= md5($a) ?>')"><i class="fas fa-times"></i></button>
                </div>
                <?php endforeach; ?>
                <?php if(empty($archivos)): ?>
                    <p style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); font-size: 0.85rem;" id="noImagesMsg">No hay imágenes en la carpeta.</p>
                <?php endif; ?>
            </div>
        </div>

        <!-- Panel 2: Motor Python (Generación) -->
        <div class="card" style="display: flex; flex-direction: column;">
            <h3 class="card-title"><i class="fas fa-cogs"></i> 2. Auto-Generación Inteligente</h3>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px;">
                Define los parámetros estéticos del informe. Al ejecutar, Inteligencia Artificial extraerá métricas precisas.
            </p>

            <form id="generadorForm">
                <div class="form-group">
                    <label>Periodo o Campaña</label>
                    <input type="text" id="periodoStr" placeholder="Ej. Abril 2026 / Campaña Feria" required>
                </div>
                <div class="form-group">
                    <label>Región Geográfica (Subtítulo)</label>
                    <input type="text" id="lugarStr" value="Tlaxcala, México" required>
                </div>

                <div style="flex-grow: 1;"></div>

                <button type="button" class="btn-submit" id="btnRun" onclick="ejecutarPython()" <?= empty($archivos) ? 'disabled style="opacity:0.5;"' : '' ?>>
                    <i class="fas fa-bolt"></i> Fabricar Reporte
                </button>
            </form>

            <!-- Consola -->
            <div id="console-container" style="margin-top: 20px;">
                <div id="console-header">Terminal Python [Log en Vivo]</div>
                <div id="console-output"></div>
            </div>

        </div>
    </div>
</div>

<script>
    const clienteId = document.getElementById('cliente_id').value;
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadStatus = document.getElementById('uploadStatus');

    // Drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles, false);

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        uploadFiles(files);
    }

    function handleFiles() {
        uploadFiles(fileInput.files);
    }

    function uploadFiles(files) {
        if(files.length === 0) return;
        uploadStatus.innerText = "Subiendo archivo(s)...";

        let formData = new FormData();
        formData.append("cliente_id", clienteId);
        for(let i = 0; i < files.length; i++){
            formData.append("evidencia[]", files[i]);
        }

        fetch('upload_evidencia.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                uploadStatus.innerHTML = "<span style='color: #4CAF50;'><i class='fas fa-check'></i> ¡Operación exitosa! Recarga la página.</span>";
                setTimeout(() => window.location.reload(), 1500);
            } else {
                uploadStatus.innerHTML = "<span style='color: red;'>Error: " + data.message + "</span>";
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = "<span style='color: red;'>Error en la red.</span>";
        });
    }

    function borrarEvidencia(filename, thumbId) {
        if(!confirm("¿Eliminar archivo: " + filename + "?")) return;
        
        let formData = new FormData();
        formData.append("cliente_id", clienteId);
        formData.append("borrar_archivo", filename);

        fetch('upload_evidencia.php', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                document.getElementById('thumb_' + thumbId).remove();
            }
        });
    }

    function ejecutarPython() {
        const periodo = document.getElementById('periodoStr').value;
        const lugar = document.getElementById('lugarStr').value;
        
        if(!periodo) { alert("¡El periodo es obligatorio!"); return; }

        const btn = document.getElementById('btnRun');
        const consoleContainer = document.getElementById('console-container');
        const consoleOutput = document.getElementById('console-output');

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ejecutando...';
        consoleContainer.style.display = 'flex';
        consoleOutput.innerHTML = "Iniciando Pipeline de Inteligencia Artificial...\nConectando módulos...\n";

        let formData = new FormData();
        formData.append("cliente_id", clienteId);
        formData.append("periodo", periodo);
        formData.append("lugar", lugar);

        // Envío asíncrono
        fetch('generar_reporte_ajax.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-bolt"></i> Fabricar Reporte';
            consoleOutput.innerHTML += "\n--- OUTPUT DEL MOTOR ---\n" + data.log;
            
            if(data.status === 'success') {
                consoleOutput.innerHTML += "\n\n[SISTEMA]: ✅ Reporte Generado y Registrado en la Base de Datos.";
                consoleOutput.style.color = "#FFD700";
            } else {
                consoleOutput.innerHTML += "\n\n[SISTEMA]: ❌ Error reportado.";
                consoleOutput.style.color = "red";
            }
        })
        .catch(err => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Fallo general';
            consoleOutput.innerHTML += "\n\nError de conexión con generador_reporte_ajax.php";
        });
    }
</script>

</body>
</html>
