<?php
require_once '../config.php';

// Verificar el acceso
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    header("Location: ../login.php");
    exit;
}

// Obtener todos los clientes
$stmt = $pdo->query("SELECT * FROM usuarios WHERE rol = 'cliente' ORDER BY fecha_registro DESC");
$clientes = $stmt->fetchAll();

// Verificar si hay mensajes en la URL
$msg = $_GET['msg'] ?? '';
$type = $_GET['type'] ?? 'success'; // success, error
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Intlax.cloud | Cartera de Clientes</title>
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
        header.dash-header { padding: 30px 0; margin-bottom: 30px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        
        .logo-font { font-family: 'Anton', sans-serif; font-size: 1.5rem; letter-spacing: 1px; }
        .logo-font span { color: var(--primary); }
        
        .action-btn { background: none; border: 1px solid var(--border-color); color: var(--text-main); padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; transition: 0.3s; text-decoration: none; }
        .action-btn:hover { border-color: var(--primary); color: var(--primary); }

        .container { max-width: 1200px; margin: 0 auto; width: 100%; }
        .page-title { font-size: 1.8rem; font-weight: 300; margin-bottom: 25px; color: var(--text-muted); }
        .page-title strong { color: #fff; font-weight: 800; }

        .system-msg { padding: 15px; border-radius: 6px; margin-bottom: 25px; font-size: 0.9rem; }
        .msg-success { background-color: rgba(46, 125, 50, 0.2); border: 1px solid #2e7d32; color: #81c784; }
        .msg-error { background-color: rgba(211, 47, 47, 0.2); border: 1px solid #d32f2f; color: #e57373; }

        .grid-layout { display: grid; grid-template-columns: 1fr 2fr; gap: 30px; }
        @media (max-width: 900px) { .grid-layout { grid-template-columns: 1fr; } }
        
        .card { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 30px; }
        .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 20px; color: var(--primary); text-transform: uppercase; font-family: 'Anton', sans-serif; letter-spacing: 1px; }

        /* Formulario */
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid var(--border-color); background-color: #000; color: #fff; font-size: 0.95rem; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--primary); }
        .btn-submit { width: 100%; background-color: var(--primary); color: #000; font-weight: 800; padding: 12px; border: none; border-radius: 6px; margin-top: 10px; cursor: pointer; text-transform: uppercase; transition: 0.2s; }
        .btn-submit:hover { filter: brightness(1.1); transform: translateY(-2px); }
        .btn-clear { background: transparent; color: var(--text-muted); border: 1px solid var(--border-color); padding: 8px; width: 100%; margin-top: 10px; border-radius: 6px; cursor: pointer; }
        .btn-clear:hover { color: #fff; }

        /* Tabla */
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
        th { color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; background-color: rgba(0,0,0,0.2); }
        tr:hover { background-color: rgba(255,215,0,0.02); }
        
        .badge { padding: 4px 8px; font-size: 0.7rem; border-radius: 12px; font-weight: 600; text-transform: uppercase; }
        .badge-gov { background: rgba(56, 142, 60, 0.2); color: #81c784; border: 1px solid #388e3c; }
        .badge-priv { background: rgba(255, 152, 0, 0.2); color: #ffb74d; border: 1px solid #f57c00; }
        
        .btn-edit { background: transparent; color: var(--primary); border: 1px solid var(--primary); padding: 5px 10px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; transition: 0.2s; }
        .btn-edit:hover { background: var(--primary); color: #000; }
    </style>
</head>
<body>

    <div id="dashboard-screen">
        <div class="container">
            <header class="dash-header">
                <div class="logo-font">INTLAX<span>.CLOUD</span> ALFA</div>
                <div>
                    <a href="dashboard.php" class="action-btn" style="margin-right: 10px;"><i class="fas fa-arrow-left"></i> Volver a Bóveda</a>
                    <a href="../logout.php" class="action-btn">Salir <i class="fas fa-sign-out-alt"></i></a>
                </div>
            </header>

            <h2 class="page-title"><i class="fas fa-users" style="color: var(--primary);"></i> Cartera Institucional de <strong>Clientes</strong></h2>

            <?php if ($msg): ?>
                <div class="system-msg msg-<?= htmlspecialchars($type) ?>">
                    <?php if($type=='success'): ?><i class="fas fa-check-circle"></i><?php else: ?><i class="fas fa-exclamation-triangle"></i><?php endif; ?> 
                    <?= htmlspecialchars($msg) ?>
                </div>
            <?php endif; ?>

            <div class="grid-layout">
                
                <!-- Panel Formulario -->
                <div class="card">
                    <h3 class="card-title" id="form-title"><i class="fas fa-plus-circle"></i> Alta de Cliente</h3>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px;">Llena los datos para generar un nuevo perfil en el sistema. Los accesos serán automáticos.</p>
                    
                    <form action="crud_clientes.php" method="POST" id="clientForm">
                        <input type="hidden" name="accion" value="guardar">
                        <input type="hidden" name="cliente_id" id="cliente_id" value="">

                        <div class="form-group">
                            <label>Nombre / Razón Social *</label>
                            <input type="text" name="nombre" id="nombre" placeholder="Ej. Gobierno de Tlaxcala" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Tipo de Cuenta *</label>
                            <select name="tipo_organizacion" id="tipo_organizacion" required>
                                <option value="empresa_privada">Empresa Privada / Comercial</option>
                                <option value="gobierno">Gobierno / Institucional</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Cargo / Dependencia (Opt)</label>
                            <input type="text" name="dependencia_cargo" id="dependencia_cargo" placeholder="Ej. Presidencia Municipal">
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div class="form-group">
                                <label>Teléfono (WhatsApp)</label>
                                <input type="text" name="telefono" id="telefono" placeholder="+52...">
                            </div>
                            <div class="form-group">
                                <label>Correo Electrónico</label>
                                <input type="email" name="email_contacto" id="email_contacto" placeholder="correo@...">
                            </div>
                        </div>

                        <hr style="border: 0; border-top: 1px dashed var(--border-color); margin: 20px 0;">

                        <div class="form-group">
                            <label>ID de Acceso (Usuario) *</label>
                            <input type="text" name="username" id="username" placeholder="Identificador único, ej. tlaxcala26" required>
                        </div>

                        <div class="form-group">
                            <label>Contraseña de Acceso</label>
                            <input type="password" name="password" id="password" placeholder="Requerida para clientes nuevos">
                            <small style="color: var(--text-muted); font-size: 0.75rem;">Nota: Si es edición, déjala en blanco para NO cambiarla.</small>
                        </div>

                        <button type="submit" class="btn-submit"><i class="fas fa-save"></i> Guardar Cliente</button>
                        <button type="button" class="btn-clear" onclick="resetForm()" id="btnReset" style="display:none;"><i class="fas fa-undo"></i> Cancelar Edición</button>
                    </form>
                </div>

                <!-- Tabla de Clientes Activos -->
                <div class="card">
                    <h3 class="card-title"><i class="fas fa-list"></i> Clientes Registrados</h3>
                    
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Organización</th>
                                    <th>ID Acceso (User)</th>
                                    <th>Contacto</th>
                                    <th>Tipo</th>
                                    <th>Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($clientes as $c): ?>
                                <tr>
                                    <td>
                                        <strong><?= htmlspecialchars($c['nombre']) ?></strong><br>
                                        <span style="font-size: 0.8rem; color: var(--text-muted);"><?= htmlspecialchars($c['dependencia_cargo'] ?? '') ?></span>
                                    </td>
                                    <td style="color: var(--primary);"><i class="fas fa-user-circle"></i> <?= htmlspecialchars($c['username']) ?></td>
                                    <td style="font-size: 0.85rem;">
                                        <?php if($c['telefono']): ?><i class="fab fa-whatsapp" style="color: #4CAF50;"></i> <?= htmlspecialchars($c['telefono']) ?><br><?php endif; ?>
                                        <?php if($c['email_contacto']): ?><i class="fas fa-envelope"></i> <?= htmlspecialchars($c['email_contacto']) ?><?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if($c['tipo_organizacion'] == 'gobierno'): ?>
                                            <span class="badge badge-gov">Gobierno</span>
                                        <?php else: ?>
                                            <span class="badge badge-priv">Privado</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <!-- Botón Editar que carga los datos en el Formulario -->
                                        <button onclick='loadUserData(<?= json_encode([
                                            "id" => $c["id"],
                                            "nombre" => $c["nombre"],
                                            "username" => $c["username"],
                                            "tipo_organizacion" => $c["tipo_organizacion"],
                                            "dependencia_cargo" => $c["dependencia_cargo"] ?? "",
                                            "telefono" => $c["telefono"] ?? "",
                                            "email_contacto" => $c["email_contacto"] ?? ""
                                        ]) ?>)' class="btn-edit"><i class="fas fa-pen"></i> Ajustar</button>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        function loadUserData(data) {
            document.getElementById('form-title').innerHTML = '<i class="fas fa-pen-nib"></i> Editando Cliente';
            document.getElementById('cliente_id').value = data.id;
            document.getElementById('nombre').value = data.nombre;
            document.getElementById('tipo_organizacion').value = data.tipo_organizacion;
            document.getElementById('dependencia_cargo').value = data.dependencia_cargo;
            document.getElementById('telefono').value = data.telefono;
            document.getElementById('email_contacto').value = data.email_contacto;
            document.getElementById('username').value = data.username;
            document.getElementById('password').required = false; // Ya que si lo deja en blanco no se cambia
            
            document.getElementById('btnReset').style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function resetForm() {
            document.getElementById('form-title').innerHTML = '<i class="fas fa-plus-circle"></i> Alta de Cliente';
            document.getElementById('clientForm').reset();
            document.getElementById('cliente_id').value = '';
            document.getElementById('password').required = true;
            document.getElementById('btnReset').style.display = 'none';
        }
    </script>
</body>
</html>
