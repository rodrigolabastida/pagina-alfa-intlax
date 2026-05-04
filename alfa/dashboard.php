<?php
require_once '../config.php';

// Verificar acceso empresa
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    header("Location: ../login.php");
    exit;
}

// Obtener reportes
$stmt = $pdo->query("SELECT r.*, u.nombre as cliente_nombre FROM reportes r JOIN usuarios u ON r.cliente_id = u.id ORDER BY r.fecha_generacion DESC");
$reportes = $stmt->fetchAll();

// Métrica global
$total_vistas = 0;
foreach($reportes as $r) {
    if ($r['estado'] === 'autorizado') {
        $total_vistas += $r['visualizaciones'];
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Intlax.cloud | Bóveda ALFA</title>
    <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --bg-dark: #0a0a0a;
            --bg-card: #141414;
            --primary: #FFD700;
            --text-main: #f5f5f5;
            --text-muted: #888;
            --border-color: #333;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }
        
        #dashboard-screen { padding: 0 20px 60px; }
        header.dash-header { padding: 30px 0; margin-bottom: 40px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        
        .logo-font { font-family: 'Anton', sans-serif; font-size: 1.5rem; letter-spacing: 1px; }
        .logo-font span { color: var(--primary); }
        
        .action-btn { background: none; border: 1px solid var(--border-color); color: var(--text-main); padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; transition: 0.3s; text-decoration: none; }
        .action-btn:hover { border-color: var(--primary); color: var(--primary); }
        .logout-btn:hover { border-color: #ff4444; color: #ff4444; }

        .container { max-width: 1000px; margin: 0 auto; width: 100%; }
        .page-title { font-size: 1.8rem; font-weight: 300; margin-bottom: 30px; color: var(--text-muted); }
        .page-title strong { color: #fff; font-weight: 800; }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-bottom: 30px; }

        .card { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 30px; }
        .card-icon { font-size: 2rem; color: var(--primary); margin-bottom: 20px; }
        .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; }

        .btn-action { display: inline-block; background-color: var(--primary); color: #000; font-weight: 700; padding: 12px 20px; border-radius: 8px; text-decoration: none; text-align: center; width: 100%; cursor: pointer; border: none; font-size: 1rem; }
        .btn-action:hover { filter: brightness(1.1); }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
        th { color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }
        
        .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
        .status-borrador { background-color: #444; color: #fff; }
        .status-autorizado { background-color: #2e7d32; color: #fff; }

        #console-output { background-color: #000; color: #0f0; font-family: monospace; padding: 15px; border-radius: 8px; height: 150px; overflow-y: auto; font-size: 0.8rem; margin-top: 15px; display: none; white-space: pre-wrap; }
    </style>
</head>
<body>

    <div id="dashboard-screen">
        <div class="container">
            <header class="dash-header">
                <div class="logo-font">INTLAX<span>.CLOUD</span> ALFA</div>
                <div>
                    <a href="clientes.php" class="action-btn" style="margin-right: 10px;"><i class="fas fa-users"></i> Gestor de Clientes</a>
                    <a href="boveda.php" class="action-btn" style="margin-right: 10px;"><i class="fas fa-vault"></i> Bóveda</a>
                    <a href="../logout.php" class="action-btn logout-btn">Cerrar Sesión <i class="fas fa-sign-out-alt"></i></a>
                </div>
            </header>

            <h2 class="page-title">Centro de Mando, <strong><?= htmlspecialchars($_SESSION['nombre']) ?></strong>.</h2>

            <div class="grid">
                <div class="card">
                    <div class="card-icon"><i class="fas fa-robot"></i></div>
                    <h3 class="card-title">Motor de Generación Python</h3>
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 15px;">Ejecutar el script `generador_reportes.py` para procesar Testigos de las carpetas y extraer métricas automáticas.</p>
                    <button class="btn-action" onclick="runScript()" id="btn-run"><i class="fas fa-play"></i> Iniciar Generación</button>
                    <div id="console-output"></div>
                </div>

                <div class="card">
                    <div class="card-icon"><i class="fas fa-chart-line"></i></div>
                    <h3 class="card-title">Métricas Globales (Autorizadas)</h3>
                    <div style="font-size: 3rem; font-weight: bold; color: #fff; line-height: 1;"><?= number_format($total_vistas) ?></div>
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin-top: 5px;">Visualizaciones este mes en cuentas de clientes</p>
                </div>
            </div>

            <div class="card" style="margin-bottom: 50px;">
                <h3 class="card-title"><i class="fas fa-folder-open" style="color: var(--primary); margin-right: 10px;"></i> Gestión de Reportes Generados</h3>
                
                <?php if (count($reportes) > 0): ?>
                <table>
                    <thead>
                        <tr>
                            <th>Periodo</th>
                            <th>Cliente</th>
                            <th>Archivo</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach($reportes as $r): ?>
                        <tr>
                            <td><?= htmlspecialchars($r['mes_periodo']) ?></td>
                            <td><?= htmlspecialchars($r['cliente_nombre']) ?></td>
                            <td><a href="../reportes/<?= htmlspecialchars($r['nombre_archivo']) ?>" target="_blank" style="color: var(--primary); text-decoration: none;"><i class="fas fa-external-link-alt"></i> HTML</a></td>
                            <td><span class="status-badge status-<?= $r['estado'] ?>"><?= strtoupper($r['estado']) ?></span></td>
                            <td>
                                <?php if ($r['estado'] === 'borrador'): ?>
                                    <form action="autorizar.php" method="POST" style="display:inline;">
                                        <input type="hidden" name="reporte_id" value="<?= $r['id'] ?>">
                                        <button type="submit" style="background:#2e7d32; color:#fff; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;"><i class="fas fa-check"></i> Autorizar</button>
                                    </form>
                                <?php else: ?>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">Publicado en panel cliente</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                <?php else: ?>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">No hay reportes indexados en la base de datos por el momento. Cuando el generador corra las inserciones ocurrirán.</p>
                <?php endif; ?>
            </div>
            
        </div>
    </div>

    <script>
        function runScript() {
            const btn = document.getElementById('btn-run');
            const cons = document.getElementById('console-output');
            
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ejecutando motor OCR...';
            btn.disabled = true;
            cons.style.display = 'block';
            cons.innerHTML = '>> Iniciando script_generador_reportes.py...\n';

            fetch('run_script.php')
            .then(response => response.json())
            .then(data => {
                let current_log = (data.log) ? data.log : "";
                cons.innerHTML += current_log + '\n';
                if(data.status === 'success') {
                    cons.innerHTML += '>> Proceso FINALIZADO con éxito.\n';
                } else {
                    cons.innerHTML += '>> ALERTA: ' + data.message + '\n';
                }
            })
            .catch(error => {
                cons.innerHTML += '>> ERROR DE SERVIDOR: ' + error + '\n';
            })
            .finally(() => {
                btn.innerHTML = '<i class="fas fa-play"></i> Iniciar Generación';
                btn.disabled = false;
            });
        }
    </script>
</body>
</html>
