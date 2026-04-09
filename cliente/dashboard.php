<?php
require_once '../config.php';

// Verificar acceso cliente
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'cliente') {
    header("Location: ../login.php");
    exit;
}

$cliente_id = $_SESSION['usuario_id'];

// Obtener reportes autorizados de este cliente
$stmt = $pdo->prepare("SELECT * FROM reportes WHERE cliente_id = ? AND estado = 'autorizado' ORDER BY fecha_generacion DESC");
$stmt->execute([$cliente_id]);
$reportes = $stmt->fetchAll();

$reporte_actual = count($reportes) > 0 ? $reportes[0] : null;

// Obtener todas las vistas del mes actual/ultimo
$total_visualizaciones = 0;
$total_espectadores = 0;
$total_interacciones = 0;

if ($reporte_actual) {
    // Si queremos sumar todo el historico o solo el mes, tomamos el actual como base
    $total_visualizaciones = $reporte_actual['visualizaciones'];
    $total_espectadores = $reporte_actual['espectadores'];
    $total_interacciones = $reporte_actual['interacciones'];
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Panel de Cliente | Intlax.cloud</title>
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
        
        #dashboard-screen { padding: 0 20px 60px; }
        header.dash-header { padding: 30px 0; margin-bottom: 40px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        
        .logo-font { font-family: 'Anton', sans-serif; font-size: 1.5rem; letter-spacing: 1px; }
        .logo-font span { color: var(--primary); }
        
        .logout-btn { background: none; border: 1px solid var(--border-color); color: var(--text-main); padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; transition: 0.3s; text-decoration: none; }
        .logout-btn:hover { border-color: #ff4444; color: #ff4444; }

        .container { max-width: 1000px; margin: 0 auto; width: 100%; }
        .page-title { font-size: 1.8rem; font-weight: 300; margin-bottom: 30px; color: var(--text-muted); }
        .page-title strong { color: #fff; font-weight: 800; }

        .grid-header { display: grid; grid-template-columns: 2fr 1fr; gap: 25px; margin-bottom: 30px; }
        @media (max-width: 768px) { .grid-header { grid-template-columns: 1fr; } }
        
        .card { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 30px; }
        .card-highlight { border-color: var(--primary); background: linear-gradient(135deg, #111 0%, #1a1705 100%); }
        
        .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; color: var(--primary); text-transform: uppercase; font-family: 'Anton', sans-serif; letter-spacing: 1px; }

        .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px; text-align: center; }
        .metric-box { background-color: var(--bg-surface); padding: 15px; border-radius: 8px; border: 1px solid #222; }
        .metric-val { font-size: 1.5rem; font-weight: bold; color: #fff; }
        .metric-lbl { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-top: 5px; }

        .btn-action { display: inline-block; background-color: var(--primary); color: #000; font-weight: 700; padding: 12px 20px; border-radius: 8px; text-decoration: none; text-align: center; cursor: pointer; border: none; font-size: 0.9rem; transition: 0.2s; }
        .btn-action:hover { filter: brightness(1.1); transform: translateY(-2px); }
        
        .btn-outline { background: transparent; border: 1px solid var(--border-color); color: #fff; }
        .btn-outline:hover { border-color: var(--primary); color: var(--primary); }

        .history-list { list-style: none; margin-top: 15px; }
        .history-list li { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px dashed var(--border-color); }
        .history-list li:last-child { border-bottom: none; }
        .history-link { color: var(--text-main); text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
        .history-link:hover { color: var(--primary); }

    </style>
</head>
<body>

    <div id="dashboard-screen">
        <div class="container">
            <header class="dash-header">
                <div class="logo-font">INTLAX<span>.CLOUD</span></div>
                <a href="../logout.php" class="logout-btn">Salir <i class="fas fa-sign-out-alt"></i></a>
            </header>

            <h2 class="page-title">Bienvenido, <strong><?= htmlspecialchars($_SESSION['nombre']) ?></strong>.</h2>

            <div class="grid-header">
                <!-- Reporte Principal -->
                <div class="card card-highlight">
                    <h3 class="card-title"><i class="fas fa-file-invoice-dollar" style="margin-right: 8px;"></i> Reporte Interactivo Vigente</h3>
                    
                    <?php if ($reporte_actual): ?>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <div>
                                <p style="font-size: 1.1rem; color: #fff; font-weight: 600;"><?= htmlspecialchars($reporte_actual['mes_periodo']) ?></p>
                                <p style="font-size: 0.85rem; color: var(--text-muted);">Actualizado automáticamente</p>
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <a href="../reportes/<?= htmlspecialchars($reporte_actual['nombre_archivo']) ?>" target="_blank" class="btn-action"><i class="fas fa-desktop"></i> Ver Interactivo</a>
                            </div>
                        </div>

                        <!-- KPIs -->
                        <div style="border-top: 1px solid rgba(255, 215, 0, 0.2); padding-top: 20px; margin-top: 20px;">
                            <p style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase;">Indicadores Clave del Mes</p>
                            <div class="metric-grid">
                                <div class="metric-box">
                                    <div class="metric-val"><?= number_format($total_visualizaciones) ?></div>
                                    <div class="metric-lbl">Visualizaciones</div>
                                </div>
                                <div class="metric-box">
                                    <div class="metric-val"><?= number_format($total_espectadores) ?></div>
                                    <div class="metric-lbl">Espectadores</div>
                                </div>
                                <div class="metric-box">
                                    <div class="metric-val"><?= number_format($total_interacciones) ?></div>
                                    <div class="metric-lbl">Interacciones</div>
                                </div>
                            </div>
                        </div>
                    <?php else: ?>
                        <p style="color: var(--text-muted);">Aún no hay reportes autorizados para este periodo.</p>
                    <?php endif; ?>
                </div>

                <!-- Historial y Herramientas -->
                <div style="display: flex; flex-direction: column; gap: 25px;">
                    <div class="card">
                        <h3 class="card-title"><i class="fas fa-history" style="margin-right: 8px; color: var(--text-muted);"></i> Archivo Histórico</h3>
                        <?php if (count($reportes) > 1): ?>
                            <ul class="history-list">
                                <?php for($i = 1; $i < count($reportes); $i++): ?>
                                <li>
                                    <span style="font-size: 0.9rem; font-weight: 600;"><?= htmlspecialchars($reportes[$i]['mes_periodo']) ?></span>
                                    <a href="../reportes/<?= htmlspecialchars($reportes[$i]['nombre_archivo']) ?>" target="_blank" class="history-link"><i class="fas fa-external-link-alt"></i> Ver</a>
                                </li>
                                <?php endfor; ?>
                            </ul>
                        <?php elseif (count($reportes) === 1): ?>
                            <p style="font-size: 0.85rem; color: var(--text-muted);">Solo hay un reporte disponible en este momento.</p>
                        <?php else: ?>
                            <p style="font-size: 0.85rem; color: var(--text-muted);">El historial está vacío.</p>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
            
        </div>
    </div>

</body>
</html>
