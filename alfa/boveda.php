<?php
require_once '../config.php';

// Verificar acceso empresa
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'empresa') {
    header("Location: ../login.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Bóveda de Clientes Intlax - Acceso exclusivo a reportes ejecutivos y métricas de desempeño.">
    <title>Bóveda de Clientes | Intlax.claud</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@300;400;700;900&display=swap" rel="stylesheet">

    <style>
        :root {
            --dark-bg: #0a0a0a;
            --surface-bg: #111111;
            --card-bg: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #a1a1aa;
            --yellow-accent: #FFD700;
            --status-active: #10b981;
            --status-pending: #f59e0b;
            --border-color: #222222;
        }

        body {
            font-family: 'Montserrat', sans-serif;
            margin: 0; padding: 0;
            background-color: var(--dark-bg);
            color: var(--text-primary);
            line-height: 1.6;
        }

        h1, h2, h3, h4, .logo-font {
            font-family: 'Anton', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .text-yellow { color: var(--yellow-accent); }
        a { text-decoration: none; color: inherit; transition: 0.3s; }

        /* --- HEADER --- */
        header {
            background-color: #000;
            color: white; padding: 20px;
            display: flex; justify-content: space-between; align-items: center;
            position: sticky; top: 0; z-index: 1000;
            border-bottom: 2px solid #222;
        }

        .menu-btn {
            font-size: 1.8rem; color: var(--yellow-accent);
            cursor: pointer; z-index: 1002;
        }

        .nav-menu {
            position: fixed; top: 0; right: -320px;
            width: 300px; height: 100vh;
            background-color: #0c0c0c;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            transition: 0.4s ease-in-out; z-index: 1001;
            border-left: 2px solid var(--yellow-accent);
        }
        .nav-menu.active { right: 0; }
        .nav-menu ul li { margin: 25px 0; text-align: center; list-style: none; }
        .nav-menu ul li a { font-size: 1.5rem; font-family: 'Anton', sans-serif; text-transform: uppercase; }
        .nav-menu ul li a:hover { color: var(--yellow-accent); }
        
        .nav-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); z-index: 999;
            opacity: 0; visibility: hidden; transition: 0.3s;
            backdrop-filter: blur(4px);
        }
        .nav-overlay.active { opacity: 1; visibility: visible; }

        /* --- MAIN CONTENT --- */
        .hero-boveda {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=2000');
            background-size: cover; background-position: center;
            padding: 100px 20px; text-align: center;
            border-bottom: 2px solid var(--yellow-accent);
        }
        .hero-boveda h1 { font-size: 3.5rem; margin-bottom: 10px; }
        .hero-boveda p { font-size: 1.2rem; color: #ccc; max-width: 700px; margin: 0 auto; }

        .container { max-width: 1200px; margin: 0 auto; padding: 60px 20px; }

        .sector-title {
            display: flex; align-items: center; gap: 15px;
            font-size: 2rem; margin-bottom: 40px; border-bottom: 2px solid #222; padding-bottom: 15px;
        }
        .sector-title i { color: var(--yellow-accent); }

        .client-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 30px; margin-bottom: 80px;
        }

        .client-card {
            background-color: var(--card-bg);
            border-radius: 12px; border: 1px solid var(--border-color);
            padding: 30px; transition: transform 0.3s, border-color 0.3s;
            position: relative; overflow: hidden;
        }
        .client-card:hover { transform: translateY(-5px); border-color: var(--yellow-accent); }
        .client-card::before {
            content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
            background-color: var(--yellow-accent); opacity: 0; transition: 0.3s;
        }
        .client-card:hover::before { opacity: 1; }

        .client-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
        .client-name { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 5px; }
        
        .status-badge {
            padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800;
            text-transform: uppercase; letter-spacing: 1px;
        }
        .status-active { background-color: rgba(16, 185, 129, 0.1); color: var(--status-active); border: 1px solid var(--status-active); }
        .status-pending { background-color: rgba(245, 158, 11, 0.1); color: var(--status-pending); border: 1px solid var(--status-pending); }

        .client-info { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 25px; }

        .report-btn {
            display: block; width: 100%; padding: 12px; text-align: center;
            background-color: #222; color: white; border-radius: 6px;
            font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
            transition: 0.3s; border: 1px solid #333;
        }
        .report-btn:hover { background-color: var(--yellow-accent); color: #000; border-color: var(--yellow-accent); }
        .report-btn.disabled { opacity: 0.5; cursor: not-allowed; }

        /* --- FOOTER --- */
        footer {
            background-color: #050505; color: #777;
            padding: 40px 20px; text-align: center;
            border-top: 1px solid #111;
        }
    </style>
</head>
<body>

    <header>
        <a href="../index.html" class="logo-font" style="font-size: 1.5rem;">
            INTLAX<span class="text-yellow">.CLAUD</span>
        </a>
        <div class="menu-btn" id="menuBtn">☰</div>

        <div class="nav-overlay" id="navOverlay"></div>
        <nav class="nav-menu" id="navMenu">
            <ul>
                <li><a href="../index.html">Inicio</a></li>
                <li><a href="dashboard.php">Panel Control</a></li>
                <li><a href="boveda.php" class="text-yellow">Bóveda Intlax</a></li>
                <li><a href="../nosotros.html">Nosotros</a></li>
                <li><a href="../logout.php"><i class="fas fa-sign-out-alt"></i> Salir</a></li>
            </ul>
        </nav>
    </header>

    <section class="hero-boveda">
        <h1>Bóveda de <span class="text-yellow">Clientes</span></h1>
        <p>Ecosistema de transparencia y resultados. Accede a las métricas de impacto y reportes ejecutivos de cada proyecto.</p>
    </section>

    <div class="container">
        
        <!-- SECTOR GOBIERNO -->
        <h2 class="sector-title"><i class="fas fa-landmark"></i> Sector Gobierno</h2>
        <div class="client-grid">
            
            <!-- Calpulalpan -->
            <div class="client-card">
                <div class="client-header">
                    <div>
                        <div class="client-name">Gobierno de Calpulalpan</div>
                        <div style="font-size: 0.8rem; color: var(--yellow-accent);">Ayuntamiento Municipal</div>
                    </div>
                    <span class="status-badge status-active">Activo</span>
                </div>
                <div class="client-info">
                    Métricas de impacto social, difusión de obra pública y gestión de crisis en redes sociales.
                </div>
                <a href="../reportes/Abril/Reporte_Calpulalpan_Abril_2026.html" class="report-btn">Ver Último Reporte</a>
            </div>

            <!-- Ana Lilia Rivera -->
            <div class="client-card">
                <div class="client-header">
                    <div>
                        <div class="client-name">Senadora Ana Lilia Rivera</div>
                        <div style="font-size: 0.8rem; color: var(--yellow-accent);">Senado de la República</div>
                    </div>
                    <span class="status-badge status-active">Activo</span>
                </div>
                <div class="client-info">
                    Reporte de alcance legislativo, interacción ciudadana y posicionamiento de agenda nacional.
                </div>
                <a href="../reportes/Abril/Reporte_Ana_Lilia_Rivera_Abril_2026.html" class="report-btn">Ver Último Reporte</a>
            </div>

            <!-- Españita -->
            <div class="client-card">
                <div class="client-header">
                    <div>
                        <div class="client-name">Gobierno de Españita</div>
                        <div style="font-size: 0.8rem; color: var(--yellow-accent);">Ayuntamiento Municipal</div>
                    </div>
                    <span class="status-badge status-pending">Pendiente</span>
                </div>
                <div class="client-info">
                    Estrategia de comunicación digital municipal y vinculación con la ciudadanía de Tlaxcala.
                </div>
                <a href="#" class="report-btn disabled">En Proceso</a>
            </div>

        </div>

        <!-- SECTOR COMERCIAL -->
        <h2 class="sector-title"><i class="fas fa-briefcase"></i> Sector Comercial</h2>
        <div class="client-grid">
            
            <!-- Laura Flores -->
            <div class="client-card">
                <div class="client-header">
                    <div>
                        <div class="client-name">Laura Flores</div>
                        <div style="font-size: 0.8rem; color: var(--yellow-accent);">Liderazgo & Opinión</div>
                    </div>
                    <span class="status-badge status-active">Activo</span>
                </div>
                <div class="client-info">
                    Métricas de marca personal, engagement y crecimiento de audiencia en plataformas Meta y TikTok.
                </div>
                <a href="../reportes/Abril/Reporte_Laura_Flores_Abril_2026.html" class="report-btn">Ver Último Reporte</a>
            </div>

            <!-- Ruben Becerra -->
            <div class="client-card">
                <div class="client-header">
                    <div>
                        <div class="client-name">Rubén Becerra Cerón</div>
                        <div style="font-size: 0.8rem; color: var(--yellow-accent);">Consultoría & Estrategia</div>
                    </div>
                    <span class="status-badge status-pending">Pendiente</span>
                </div>
                <div class="client-info">
                    Análisis de impacto comercial y optimización de campañas de marketing digital.
                </div>
                <a href="#" class="report-btn disabled">En Proceso</a>
            </div>

        </div>

    </div>

    <footer>
        <div class="container" style="padding: 0;">
            <p>&copy; 2026 Intlax.claud. Sistema de Gestión de Reportes Bóveda ALFA 2.0</p>
        </div>
    </footer>

    <script>
        const menuBtn = document.getElementById('menuBtn');
        const navMenu = document.getElementById('navMenu');
        const navOverlay = document.getElementById('navOverlay');

        function toggleMenu() {
            navMenu.classList.toggle('active');
            navOverlay.classList.toggle('active');
            menuBtn.innerHTML = navMenu.classList.contains('active') ? '✕' : '☰';
        }

        menuBtn.addEventListener('click', toggleMenu);
        navOverlay.addEventListener('click', toggleMenu);
    </script>
</body>
</html>
