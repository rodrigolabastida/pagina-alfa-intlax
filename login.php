<?php
require_once 'config.php';

// Si ya hay sesión iniciada, redirigir
if (isset($_SESSION['usuario_id'])) {
    if ($_SESSION['rol'] === 'empresa') {
        header("Location: alfa/dashboard.php");
        exit;
    } else {
        header("Location: cliente/dashboard.php");
        exit;
    }
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if ($username && $password) {
        $stmt = $pdo->prepare("SELECT id, nombre, password_hash, rol FROM usuarios WHERE username = ? LIMIT 1");
        $stmt->execute([$username]);
        $user = $stmt->fetch();

        if ($user && password_verify($password, $user['password_hash'])) {
            $_SESSION['usuario_id'] = $user['id'];
            $_SESSION['nombre'] = $user['nombre'];
            $_SESSION['rol'] = $user['rol'];

            if ($user['rol'] === 'empresa') {
                header("Location: alfa/dashboard.php");
                exit;
            } else {
                header("Location: cliente/dashboard.php");
                exit;
            }
        } else {
            $error = 'Credenciales incorrectas o acceso denegado.';
        }
    } else {
        $error = 'Por favor ingresa usuario y contraseña.';
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intlax.cloud | Acceso Bóveda</title>
    <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
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
        
        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .login-box {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 40px; border-radius: 12px;
            width: 100%; max-width: 400px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        }

        .login-box h1 { font-family: 'Anton', sans-serif; letter-spacing: 2px; color: var(--primary); margin-bottom: 5px; font-size: 2rem; }
        .login-box p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 30px; }

        .input-group { margin-bottom: 20px; text-align: left; }
        .input-group label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }
        .input-group input {
            width: 100%; padding: 12px 15px; border-radius: 6px;
            border: 1px solid var(--border-color); background-color: #000;
            color: #fff; font-size: 1rem; outline: none; transition: border-color 0.3s;
        }
        .input-group input:focus { border-color: var(--primary); }

        .btn-submit {
            width: 100%; background-color: var(--primary); color: #000;
            border: none; padding: 14px; border-radius: 6px;
            font-size: 1rem; font-weight: 800; cursor: pointer;
            transition: 0.3s; text-transform: uppercase; margin-top: 10px;
        }
        .btn-submit:hover { filter: brightness(1.2); }

        .error-msg { 
            color: #ff4444; font-size: 0.85rem; margin-top: 15px; 
            padding: 10px; border: 1px solid #ff4444; border-radius: 4px;
            background-color: rgba(255, 68, 68, 0.1);
        }
        
        .back-link {
            display: inline-block; margin-top: 25px; color: var(--text-muted);
            text-decoration: none; font-size: 0.85rem; transition: 0.3s;
        }
        .back-link:hover { color: var(--primary); }
    </style>
</head>
<body>

    <div class="login-box">
        <h1>BÓVEDA ALFA</h1>
        <p>Sistema de acceso inteligente.</p>
        
        <?php if ($error): ?>
            <div class="error-msg"><i class="fas fa-exclamation-triangle"></i> <?= htmlspecialchars($error) ?></div>
            <br>
        <?php endif; ?>

        <form method="POST" action="">
            <div class="input-group">
                <label>Usuario / ID</label>
                <input type="text" name="username" placeholder="Ingresa tu ID" autocomplete="off" required>
            </div>
            <div class="input-group">
                <label>Contraseña</label>
                <input type="password" name="password" placeholder="••••••••" required>
            </div>
            <button type="submit" class="btn-submit">Acceder</button>
        </form>
        
        <a href="index.html" class="back-link"><i class="fas fa-arrow-left"></i> Volver al sitio público</a>
    </div>

</body>
</html>
