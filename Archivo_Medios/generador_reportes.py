import os
import re
import csv
import json
import base64
import io
import pytesseract
from PIL import Image, ImageEnhance
from pytesseract import Output
from jinja2 import Template

# Configuración de Tesseract para macOS (Homebrew en M1/M2 o Intel)
if os.path.exists('/opt/homebrew/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
elif os.path.exists('/usr/local/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# Configuración global por defecto, sobrescribibles con argparse
PERIODO = "Marzo 2026"
PLATAFORMA = "Facebook"
LUGAR = "Calpulalpan, Tlaxcala"
CLIENTE_FORMAL = None

# Plantilla HTML con Jinja2 (Diseño Híbrido: Dark Mode en Pantalla / Claro Corporativo en Imprimir PDF)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Mensual - {{ cliente }}</title>
    <!-- Privacidad: Ocultar de buscadores -->
    <meta name="robots" content="noindex, nofollow">
    <meta name="googlebot" content="noindex">
    <!-- Fuentes y FontAwesome -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            /* Variables globales para Pantalla (DARK MODE) */
            --bg-base: #0a0a0a;
            --bg-surface: #171717;
            --bg-card: #222222;
            --text-primary: #ededed;
            --text-secondary: #a1a1aa;
            --accent: #FFD700;       /* Amarillo Institucional Intlax */
            --accent-green: #F59E0B;
            --border-color: #3f3f46;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            line-height: 1.6;
            -webkit-print-color-adjust: exact;
        }

        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .content-wrap { padding: 40px 0; }

        /* --- PORTADA --- */
        header {
            text-align: center;
            padding: 60px 20px;
            background-color: var(--bg-surface);
            border-radius: 16px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }

        header::before {
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
        }

        .intlax-branding {
            font-family: 'Montserrat', sans-serif;
            font-size: 1rem; letter-spacing: 2px;
            color: var(--text-primary);
            margin-bottom: 15px; display: block; font-weight: 900;
        }
        .intlax-branding span { color: var(--accent); }

        .main-title { font-size: 2.5rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 15px; color: var(--text-primary); }
        .subtitle { font-size: 1.8rem; font-weight: 400; color: var(--text-secondary); margin-bottom: 30px; }

        .details-badge {
            display: inline-flex; gap: 15px;
            background: var(--bg-card); padding: 10px 20px; border-radius: 30px;
            margin-bottom: 30px; border: 1px solid var(--border-color); font-size: 0.95rem;
        }
        .details-badge span { color: var(--text-secondary); }
        .details-badge strong { color: var(--text-primary); font-weight: 600; }

        .footer-header { font-size: 0.9rem; color: var(--text-secondary); border-top: 1px dashed var(--border-color); padding-top: 20px; max-width: 400px; margin: 0 auto; }

        /* --- SECCIONES GLOBALES --- */
        .section-box { background-color: var(--bg-surface); padding: 40px; border-radius: 16px; border: 1px solid var(--border-color); margin-bottom: 40px; }

        h2.section-title { font-size: 1.8rem; font-weight: 600; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); color: var(--text-primary); }

        /* --- RESUMEN GENERAL --- */
        .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        @media (max-width: 768px) { .summary-grid { grid-template-columns: 1fr; } }
        
        .summary-card {
            background-color: var(--bg-card);
            padding: 25px 20px; border-radius: 12px; text-align: center;
            border: 1px solid var(--border-color);
            transition: transform 0.3s, border-color 0.3s;
        }
        .summary-card:hover { filter: brightness(1.2); border-color: var(--border-color); }
        .summary-card .value { font-size: 2.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 5px; }
        .summary-card .label { font-size: 1rem; color: var(--text-primary); text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }

        /* --- GLOSARIO DE TÉRMINOS --- */
        .glossary-list { list-style: none; }
        .glossary-list li { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed var(--border-color); color: var(--text-secondary); }
        .glossary-list li:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        .glossary-list strong { color: var(--text-primary); display: inline-block; min-width: 150px; }

        /* --- COMPARATIVO MOM --- */
        .mom-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        @media (max-width: 768px) { .mom-grid { grid-template-columns: 1fr; } }
        .mom-card {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
        }
        .mom-label { font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;}
        .mom-value { font-size: 2rem; font-weight: 700; margin-bottom: 5px; color: var(--text-primary); }
        .mom-diff { font-size: 1.1rem; font-weight: 600; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .neutral { color: var(--text-secondary); }

        /* --- ANEXOS TESTIGOS --- */
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 30px;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 40px 0 20px 0;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .section-header h2 {
            font-size: 1.8rem;
            font-weight: 700;
        } .card {
            background-color: var(--bg-surface);
            border-radius: 12px; overflow: hidden;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.6); border-color: var(--accent); }

        .card-img-wrapper {
            width: 100%; height: 200px;
            background-color: #050505;
            display: flex; align-items: center; justify-content: center;
            border-bottom: 1px solid var(--border-color); padding: 5px;
        }
        .card img { max-width: 100%; max-height: 100%; object-fit: contain; }

        .metrics-container { padding: 15px; background-color: var(--bg-card); }
        .metric-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px dashed var(--border-color); }
        .metric-row:last-child { border-bottom: none; }
        .metric-label { font-size: 0.9rem; color: var(--text-secondary); font-weight: 500; }
        .metric-value { font-size: 1rem; font-weight: 700; color: var(--text-primary); }
        .filename-caption { font-size: 0.7rem; color: #52525b; text-align: center; margin-top: 10px; word-wrap: break-word; }
        .post-title-extract { font-size: 0.8rem; color: var(--text-primary); font-weight: 600; font-style: italic; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px dashed var(--border-color); line-height: 1.3; height: 2.6em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

        .fa-yellow { color: var(--accent); margin-right: 6px;}

        /* --- EXPORTAR / IMPRIMIR (BTNS) --- */
        .print-btn {
            display: inline-flex; align-items: center; gap: 10px; background-color: var(--accent); color: #000;
            border: none; padding: 12px 24px; border-radius: 8px; font-size: 1rem; font-weight: 700;
            cursor: pointer; transition: transform 0.2s, filter 0.2s; text-decoration: none; margin: 20px 0;
        }
        .print-btn:hover { transform: scale(1.05); filter: brightness(1.1); }

        /* --- FOOTER INTLAX (DARK) --- */
        footer {
            background-color: #050505; padding: 60px 0 20px; margin-top: 20px; border-top: 2px solid var(--accent);
        }
        .footer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 40px; margin-bottom: 40px; color: var(--text-secondary); font-size: 0.95rem; }
        .footer-col h4 { color: var(--text-primary); font-family: 'Montserrat', sans-serif; font-size: 1.1rem; margin-bottom: 20px; letter-spacing: 1px; }
        .footer-col ul { list-style: none; }
        .footer-col ul li { margin-bottom: 12px; }
        .footer-col a { color: var(--text-secondary); text-decoration: none; transition: color 0.3s; }
        .footer-col a:hover { color: var(--accent); }
        .text-accent { color: var(--accent); }

        /* ============================================================== */
        /* --- MEDIA PRINT (TEMA CLARO EXCLUSIVO DE PDF Y AHORRO) --- */
        /* ============================================================== */
        @media print {
            /* Fuerza Bruta: Fondo Blanco y Texto Negro */
            * { 
                -webkit-print-color-adjust: exact !important; 
                print-color-adjust: exact !important; 
                background-color: transparent !important; 
                color: #000000 !important;
                box-shadow: none !important;
                text-shadow: none !important;
            }
            
            body, html, .container, .section-box, .card, .summary-card, .mom-card, .metrics-container, .card-img-wrapper {
                background-color: #ffffff !important;
                background: #ffffff !important;
            }

            body { font-size: 9pt; }
            .print-btn { display: none !important; }
            header::before { background: #ca8a04 !important; height: 4px !important; }

            /* SECCIONES HORIZONTALES ESTRICTAS (Top 3, Resumen y Demografía) */
            .summary-grid, .mom-grid, .anexos-grid:first-of-type, .demograficos-grid {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important; /* Prohibir el salto de línea */
                justify-content: space-between !important;
                gap: 10px !important;
                width: 100% !important;
            }

            .summary-card, .mom-card, .anexos-grid:first-of-type .card, .demograficos-grid > div {
                width: 31% !important;
                flex: 1 !important; /* Forzar que compartan el espacio por igual */
                display: block !important;
                margin: 0 !important;
                padding: 8px !important;
                border: 1px solid #ddd !important;
                overflow: hidden !important;
            }

            /* DISEÑO COMPACTO EJECUTIVO */
            body { font-size: 8.5pt !important; line-height: 1.2 !important; }
            .container { max-width: 100% !important; padding: 0 !important; margin: 0 !important; }
            
            .section-box {
                page-break-before: auto !important;
                margin-bottom: 15px !important;
                padding: 10px !important;
                border-bottom: 1px solid #eee !important;
            }
            
            #seccion-testigos { page-break-before: always !important; padding-top: 0 !important; }
            .section-title { font-size: 11pt !important; margin-bottom: 8px !important; padding-bottom: 3px !important; }

            /* Métricas y Top 3 en 3 columnas compactas */
            .summary-grid, .mom-grid, .anexos-grid:first-of-type, .demograficos-grid {
                display: flex !important;
                flex-wrap: nowrap !important;
                gap: 8px !important;
                margin-bottom: 10px !important;
            }

            .summary-card, .mom-card, .anexos-grid:first-of-type .card, .demograficos-grid > div {
                flex: 1 !important;
                padding: 6px !important;
                border: 1px solid #ddd !important;
                background: #fff !important;
            }

            .summary-card .value { font-size: 12pt !important; }
            .summary-card .label { font-size: 7pt !important; }
            .post-title-extract { font-size: 7pt !important; height: 2.2em !important; margin-bottom: 3px !important; }

            /* Galería 2x2 Estricta (4 por página) */
            .gallery-grid {
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 10px !important;
                justify-content: space-between !important;
            }

            .gallery-grid .card {
                width: 48% !important;
                margin-bottom: 12px !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                border: 1px solid #eee !important;
                display: block !important;
            }

            .card-img-wrapper { 
                height: auto !important;
                max-height: 9.5cm !important; /* Altura crítica para que quepan 4 (2x2) */
                overflow: hidden !important;
                padding: 4px !important;
                border-bottom: 1px solid #eee !important;
            }
            
            .card img { 
                max-width: 100% !important;
                max-height: 100% !important;
                width: auto !important;
                height: auto !important;
                display: block !important;
                margin: 0 auto !important;
            }

            .metrics-container { padding: 5px !important; }
            .metric-row { padding: 2px 0 !important; font-size: 7pt !important; border-bottom: 1px dotted #ccc !important; }
            
            footer { margin-top: 10px !important; padding-top: 5px !important; border-top: 1px solid #eee !important; }
            .footer-col { font-size: 7pt !important; }

            .metrics-container { 
                border-top: 1px solid #eee !important; 
                padding: 10px !important;
                break-inside: avoid !important;
                page-break-inside: avoid !important;
                display: block !important;
            }
            .metric-row { 
                border-bottom: 1px dotted #ccc !important; 
                padding: 4px 0 !important;
                break-inside: avoid !important;
                display: flex !important;
                justify-content: space-between !important;
            }
            .post-title-extract { font-size: 8pt !important; border-bottom: 1px solid #eee !important; }
            
            /* Bordes de Podio (Top 3) */
            .card[style*="border"] { border-width: 1px !important; }
            
            footer { border-top: 1px solid #000 !important; margin-top: 20px !important; }
            .footer-grid { display: flex !important; justify-content: space-between !important; }
            .footer-col { width: 30% !important; }
        }
    </style>
</head>
<body>

<div class="container content-wrap">
    <!-- PORTADA -->
    <header>
        <span class="intlax-branding"><span class="text-accent">IN</span>TLAX.CLAUD</span>
        {% if info_cliente.entidad %}
        <div style="font-family: 'Montserrat', sans-serif; font-size: 1.2rem; color: var(--accent); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">
            {{ info_cliente.entidad }}
        </div>
        {% endif %}
        <h1 class="main-title">Reporte Ejecutivo de Desempeño</h1>
        <h2 class="subtitle">{{ cliente }}</h2>
        {% if info_cliente.dirigido_a %}
        <p style="color: var(--text-secondary); margin-top: -20px; margin-bottom: 25px; font-style: italic; font-size: 1.1rem;">
            Presentado a: {{ info_cliente.dirigido_a }}
        </p>
        {% endif %}
        
        <div class="details-badge">
            <div><span>Plataforma:</span> <strong>{{ plataforma }}</strong></div>
            <div><span>Periodo:</span> <strong>{{ periodo }}</strong></div>
        </div>
        
        <!-- Botón SUPERIOR de Imprimir -->
        <div>
            <button class="print-btn" onclick="window.print()">
                <i class="fas fa-file-pdf"></i> Guardar como PDF / Imprimir
            </button>
        </div>
        
        <div class="footer-header">Generado analíticamente por <strong>Intlax.cloud</strong><br>{{ lugar }}</div>
    </header>

    <!-- RESUMEN GENERAL -->
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-chart-line fa-yellow"></i> Desempeño Global</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <div class="value">{{ total_visualizaciones }}</div>
                <div class="label">Total Visualizaciones</div>
            </div>
            <div class="summary-card">
                <div class="value">{{ total_espectadores }}</div>
                <div class="label">Total Espectadores</div>
            </div>
            <div class="summary-card">
                <div class="value">{{ total_interacciones }}</div>
                <div class="label">Total Interacciones</div>
            </div>
        </div>
    </div>

    {% if top_posts and top_posts|length > 0 %}
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-award fa-yellow"></i> Top 3 Contenidos Destacados</h2>
        <div class="anexos-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
            {% for idx, item in enumerate_top(top_posts) %}
            <div class="card" style="border: {% if idx == 1 %}2px solid var(--accent){% elif idx == 2 %}2px solid #94a3b8{% else %}2px solid #b45309{% endif %}; position: relative;">
                
                <div style="position: absolute; top: 0; right: 0; padding: 3px 8px; border-bottom-left-radius: 6px; font-weight: bold; font-size: 0.7rem; background: {% if idx == 1 %}var(--accent); color: #000{% elif idx == 2 %}#94a3b8; color: #000{% else %}#b45309; color: #fff{% endif %}; z-index: 10; text-transform: uppercase;">
                    #{{ idx }}
                </div>

                <div class="card-img-wrapper" style="height: 160px;">
                    <img src="{{ item.relative_img_path }}" alt="Top {{ idx }}">
                </div>
                <div class="metrics-container" style="padding: 12px;">
                    <div class="post-title-extract" style="font-size: 0.75rem; height: 3em;">"{{ item.metrics.get('Titulo', '') }}"</div>
                    <div class="metric-row" style="padding: 5px 0;">
                        <span class="metric-label" style="font-size: 0.8rem;"><i class="fas fa-eye fa-yellow"></i> Vistas</span>
                        <span class="metric-value" style="font-size: 0.9rem;">{{ item._display_vis }}</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- COMPARATIVO HISTÓRICO -->
    {% if has_comparativo %}
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-rocket fa-yellow"></i> Crecimiento (vs {{ prev_period_name }})</h2>
        <div class="mom-grid">
            <div class="mom-card">
                <div class="mom-label">Visualizaciones</div>
                <div class="mom-value">{{ total_visualizaciones }}</div>
                <div class="mom-diff {{ d_vis_cls }}">
                    <i class="fas {{ d_vis_icn }}"></i> {{ diff_vis }}%
                </div>
                <div class="chart-container" style="height: 120px; margin-top: 15px;">
                    <canvas id="chartVis"></canvas>
                </div>
            </div>
            <div class="mom-card">
                <div class="mom-label">Espectadores</div>
                <div class="mom-value">{{ total_espectadores }}</div>
                <div class="mom-diff {{ d_esp_cls }}">
                    <i class="fas {{ d_esp_icn }}"></i> {{ diff_esp }}%
                </div>
                <div class="chart-container" style="height: 120px; margin-top: 15px;">
                    <canvas id="chartEsp"></canvas>
                </div>
            </div>
            <div class="mom-card">
                <div class="mom-label">Interacciones</div>
                <div class="mom-value">{{ total_interacciones }}</div>
                <div class="mom-diff {{ d_int_cls }}">
                    <i class="fas {{ d_int_icn }}"></i> {{ diff_int }}%
                </div>
                <div class="chart-container" style="height: 120px; margin-top: 15px;">
                    <canvas id="chartInt"></canvas>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- MÉTRICAS DE AUDIENCIA CSV -->
    {% if datos_publico %}
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-users fa-yellow"></i> Demografía y Alcance Geográfico</h2>

        <div class="demograficos-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            <!-- Países -->
            <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border-color);">
                <h4 style="margin-bottom: 15px; color: var(--text-primary); font-size: 0.95rem;">Distribución Continental (América)</h4>
                {% if datos_publico.paises %}
                    {% for p in datos_publico.paises %}
                    <div style="margin-bottom: 10px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:3px; font-size:0.85rem;">
                            <span>{{ p.nombre }}</span><strong>{{ p.valor }}%</strong>
                        </div>
                        <div style="width:100%; height:6px; background:var(--bg-surface); border-radius:10px; overflow:hidden;">
                            <div style="width: {{ p.valor }}%; height:100%; background: var(--accent);"></div>
                        </div>
                    </div>
                    {% endfor %}
                {% endif %}
            </div>

            <!-- Edades -->
            <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border-color);">
                <h4 style="margin-bottom: 15px; color: var(--text-primary); font-size: 0.95rem;">Sexo y Grupo de Edad</h4>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; border-bottom:1px solid var(--border-color); padding-bottom:3px; font-size:0.75rem; color:var(--text-secondary); font-weight: 600;">
                        <div>RANGO</div><div style="text-align:right;">HOMBRES</div><div style="text-align:right;">MUJERES</div>
                    </div>
                    {% for rango, vals_h in datos_publico.edades.Hombres.items() %}
                    {% set vals_m = datos_publico.edades.Mujeres[rango] %}
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; font-size:0.85rem;">
                        <div style="font-weight:600; color:var(--text-primary);">{{ rango }}</div>
                        <div style="text-align:right;">{{ vals_h }}%</div>
                        <div style="text-align:right;">{{ vals_m }}%</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Ciudades -->
            <div style="background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border-color);">
                <h4 style="margin-bottom: 15px; color: var(--text-primary); font-size: 0.95rem;">Principales Ciudades</h4>
                {% if datos_publico.ciudades %}
                    <ul style="list-style:none; padding:0;">
                    {% for c in datos_publico.ciudades %}
                        <li style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dashed var(--border-color); font-size:0.85rem;">
                            <span>{{ c.nombre }}</span><span style="color:var(--text-secondary);"><strong>{{ c.valor }}%</strong></span>
                        </li>
                    {% endfor %}
                    </ul>
                {% endif %}
            </div>
        </div>
    </div>
    {% endif %}

    <!-- ANEXOS TESTIGOS -->
    <div class="section-box" id="seccion-testigos" style="margin-bottom: 0;">
        <h2 class="section-title"><i class="fas fa-camera fa-yellow"></i> Expediente Fotográfico de Evidencias</h2>
        {% if reportes_data_meta or reportes_data_tiktok %}
        
        <div class="section-header">
            <i class="fab fa-facebook fa-2x" style="color: #1877F2;"></i>
            <h2>Testigos Meta Business Suite</h2>
        </div>
        <div class="gallery-grid">
            {% for item in reportes_data_meta %}
            <div class="card">
                <div class="card-img-wrapper">
                    <img src="{{ item.relative_img_path }}" alt="Testigo fotográfico">
                </div>
                <div class="metrics-container">
                    <div class="post-title-extract">"{{ item.metrics.get('Titulo', '') }}"</div>
                    <div class="metric-row">
                        <span class="metric-label">Visualizaciones</span>
                        <span class="metric-value">{{ item._display_vis }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Espectadores</span>
                        <span class="metric-value">{{ item._display_esp }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Interacci.</span>
                        <span class="metric-value">{{ item._display_int }}</span>
                    </div>
                    <div class="filename-caption">{{ item.filename }}</div>
                </div>
            </div>
            {% endfor %}
        </div>

        {% if reportes_data_tiktok|length > 0 %}
        <div class="section-header" style="margin-top: 60px;">
            <i class="fab fa-tiktok fa-2x" style="color: #fff;"></i>
            <h2>Testigos TikTok Studio</h2>
        </div>
        <div class="gallery-grid">
            {% for item in reportes_data_tiktok %}
            <div class="card" style="border-color: #ff0050;">
                <div class="card-img-wrapper">
                    <img src="{{ item.relative_img_path }}" alt="Testigo fotográfico">
                </div>
                <div class="metrics-container">
                    <div class="post-title-extract">"{{ item.metrics.get('Titulo', '') }}"</div>
                    <div class="metric-row">
                        <span class="metric-label">Visualizaciones</span>
                        <span class="metric-value">{{ item._display_vis }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Interacciones</span>
                        <span class="metric-value">{{ item._display_int }}</span>
                    </div>
                    <div class="metric-row" style="opacity: 0.5;">
                        <span class="metric-label">Plataforma</span>
                        <span class="metric-value">TikTok</span>
                    </div>
                    <div class="filename-caption">{{ item.filename }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% else %}
        <p style="text-align: center; color: var(--text-secondary);">No se detectaron fotografías legibles en este lote.</p>
        {% endif %}
    </div>

    <!-- Botón INFERIOR de Imprimir -->
    <div style="text-align: center; margin: 40px 0;">
        <button class="print-btn" onclick="window.print()">
            <i class="fas fa-file-pdf"></i> Guardar como PDF / Imprimir
        </button>
    </div>
</div>

<footer>
    <div class="container footer-grid">
        <div class="footer-col">
            <a href="index.html" style="text-decoration: none;">
                <span style="font-family:'Montserrat'; font-weight:900; font-size:1.6rem; color:var(--text-primary); display:block; margin-bottom:15px; letter-spacing: -1px;">
                    <span class="text-accent">IN</span>TLAX.CLAUD
                </span>
            </a>
            <p>Agencia de desarrollo web y comunicación digital.<br>Transformamos ideas en tecnología funcional desde Tlaxcala.</p>
        </div>

        <div class="footer-col">
            <h4>LEGAL</h4>
            <ul>
                <li><a href="../nosotros.html">Quiénes Somos</a></li>
                <li><a href="../calidad.html">Política de Calidad</a></li>
                <li><a href="../privacidad.html">Política de Privacidad</a></li>
            </ul>
        </div>

        <div class="footer-col">
            <h4>CONTACTO</h4>
            <ul>
                <li>📍 Tlaxcala, México</li>
                <li>📞 <a href="tel:+527491105378">749 110 5378</a></li>
                <li>✉️ contacto@intlax.claud</li>
            </ul>
        </div>
    </div>

    <div style="text-align: center; border-top: 1px solid var(--border-color); padding-top: 30px;" class="container">
        <p style="font-size: 0.9rem; color: var(--text-secondary);">
            &copy; 2026 Intlax.claud. Desarrollado en México.
        </p>
    </div>
</footer>

    {% if has_comparativo %}
    <script>
        function createMoMChart(id, label, prevVal, currVal, prevLabel, currLabel) {
            const canvas = document.getElementById(id);
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: [prevLabel, currLabel],
                    datasets: [{
                        label: label,
                        data: [prevVal, currVal],
                        backgroundColor: ['#64748b', '#f59e0b'],
                        borderColor: ['#475569', '#d97706'],
                        borderWidth: 1,
                        borderRadius: 4,
                        barThickness: 45
                    }]
                },
                options: {
                    animation: { duration: 0 },
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        tooltip: { enabled: false }
                    },
                    scales: {
                        y: { display: false, beginAtZero: true },
                        x: {
                            ticks: { color: '#000000', font: { size: 12, weight: '700' } },
                            grid: { display: false, drawBorder: false }
                        }
                    }
                }
            });

            // Convertir a imagen estática para asegurar compatibilidad con PDF
            setTimeout(() => {
                const img = document.createElement('img');
                img.src = chart.toBase64Image();
                img.style.width = '100%';
                img.style.height = '100%';
                canvas.parentNode.replaceChild(img, canvas);
            }, 100);
        }

        document.addEventListener('DOMContentLoaded', () => {
            createMoMChart('chartVis', 'Visualizaciones', {{ prev_vis }}, {{ curr_vis }}, '{{ prev_period_short }}', '{{ curr_period_short }}');
            createMoMChart('chartEsp', 'Espectadores', {{ prev_esp }}, {{ curr_esp }}, '{{ prev_period_short }}', '{{ curr_period_short }}');
            createMoMChart('chartInt', 'Interacciones', {{ prev_int }}, {{ curr_int }}, '{{ prev_period_short }}', '{{ curr_period_short }}');
        });
    </script>
    {% endif %}
</body>
</html>
"""

def preprocess_image_for_ocr(img_path):
    """
    Convierte a escala de grises y sube contraste para mejorar lectura.
    """
    img = Image.open(img_path)
    img = img.convert('L')
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(2.0)

def format_number(num):
    """ Retorna un string formateado con comas. Ej: 15400 -> '15,400' """
    return "{:,}".format(num)

MESES_MAP = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

def parse_periodo(periodo_str):
    parts = periodo_str.split(' ')
    if len(parts) == 2:
        mes = parts[0].lower()
        anio = int(parts[1])
        mes_val = MESES_MAP.get(mes, 0)
        return (anio, mes_val)
    return (0, 0)

def calculate_mom(current, previous):
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100
def get_diff_ui(diff_val):
    if diff_val > 0:
        return "positive", "fa-arrow-up"
    elif diff_val < 0:
        return "negative", "fa-arrow-down"
    return "neutral", "fa-minus"

def extract_tiktok_metrics(img_path):
    """ Extrae métricas de capturas de TikTok Studio (Resumen de Video). """
    base_metrics = {
        'Titulo': "Video de TikTok",
        'Visualizaciones': "0",
        'Espectadores': "0",
        'Interacciones': "0"
    }
    try:
        img = Image.open(img_path).convert('L')
        data = pytesseract.image_to_data(img, lang='spa+eng', config='--psm 6', output_type=Output.DICT)
        
        words = []
        for i in range(len(data['text'])):
            w_text = data['text'][i].lower().strip()
            if w_text:
                words.append({
                    "text": w_text,
                    "left": data['left'][i],
                    "top": data['top'][i],
                    "width": data['width'][i],
                    "height": data['height'][i]
                })

        # TikTok Studio Layout:
        # 1. "Visualizaciones del video" -> El número está justo DEBAJO
        # 2. Iconos arriba a la derecha: Likes, Comentarios, Compartidos, Guardados
        
        mapping = {
            "Visualizaciones": ["visualizaciones", "vistas", "views", "reproducciones"],
            "Likes": ["gusta", "likes", "corazón"],
            "Comments": ["comentarios", "comments"],
            "Shares": ["compartidos", "shares"],
            "Saves": ["guardados", "saves"]
        }
        
        extracted_vals = {"Visualizaciones": "0", "Likes": "0", "Comments": "0", "Shares": "0", "Saves": "0"}
        
        for m_key, kws in mapping.items():
            h_rect = None
            for w in words:
                if any(kw in w["text"] for kw in kws):
                    h_rect = w
                    break
            
            if h_rect:
                # Buscar número arriba o abajo (TikTok a veces los pone arriba de la palabra)
                for w in words:
                    if abs(w["left"] + w["width"]/2 - (h_rect["left"] + h_rect["width"]/2)) < 80:
                        if abs(w["top"] - h_rect["top"]) < 100 and re.search(r'\d', w["text"]):
                            extracted_vals[m_key] = w["text"]
                            break
        
        total_int = parse_metric_to_int(extracted_vals["Likes"]) + parse_metric_to_int(extracted_vals["Comments"]) + \
                    parse_metric_to_int(extracted_vals["Shares"]) + parse_metric_to_int(extracted_vals["Saves"])
        
        base_metrics['Visualizaciones'] = extracted_vals["Visualizaciones"]
        base_metrics['Espectadores'] = extracted_vals["Visualizaciones"]
        base_metrics['Interacciones'] = str(total_int)
        
        # --- EXTRACCIÓN DE TÍTULO TIKTOK (Surgical Anchor) ---
        anchor_w = None
        for w in words:
            if "publicado" in w["text"].lower():
                anchor_w = w
                break
        
        if anchor_w:
            # El título está justo ARRIBA del anchor
            title_candidates = []
            for w in words:
                if (anchor_w["top"] - 180) < w["top"] < (anchor_w["top"] - 5):
                    if w["left"] > 150: # Evitar sidebar
                        title_candidates.append(w)
            
            if title_candidates:
                title_candidates.sort(key=lambda x: (x["top"] // 20, x["left"]))
                base_metrics['Titulo'] = " ".join([c["text"] for c in title_candidates[:15]])
        
        # Fallback si no hay anchor
        if base_metrics['Titulo'] == "Video de TikTok":
            potential_titles = [w["text"] for w in words if 300 < w["top"] < 600 and len(w["text"]) > 4]
            if potential_titles:
                base_metrics['Titulo'] = " ".join(potential_titles[:10])

        return base_metrics
    except Exception as e:
        print(f"Error procesando tiktok {img_path}: {e}")
        return base_metrics

def parse_metric_to_int(val_str):
    """ Convierte cadenas como '1.5k', '5 mil', '1,200', '100,1 mil' a enteros matemáticos. """
    if not val_str or val_str == "N/D":
        return 0
    
    # Limpieza: remover ruidos y normalizar
    val = str(val_str).lower().replace(' ', '').replace('\n', '')
    # Eliminar duplicados de 'mil'
    while 'milmil' in val: val = val.replace('milmil', 'mil')
    val = val.strip()
    
    try:
        # CASO 1: Tiene multiplicador (k o mil)
        if 'k' in val or 'mil' in val:
            v_clean = val.replace('k', '').replace('mil', '').strip()
            # En este caso, tanto la coma como el punto suelen ser decimales (14,1 mil o 14.1 mil)
            v_clean = v_clean.replace(',', '.')
            
            # Si hay múltiples puntos, dejar solo el primero
            if v_clean.count('.') > 1:
                parts = v_clean.split('.')
                v_clean = parts[0] + "." + "".join(parts[1:])
                
            return int(float(v_clean) * 1000)
        
        # CASO 2: Número sin multiplicador explícito
        else:
            # Si hay comas y puntos, la coma es miles y el punto es decimal (formato estándar)
            if ',' in val and '.' in val:
                v_clean = val.replace(',', '')
                return int(float(v_clean))
            
            # Si hay solo un separador
            if ',' in val:
                parts = val.split(',')
                if len(parts[-1]) == 3: # 1,200 -> 1200
                    return int(val.replace(',', ''))
                else: # 14,1 -> 14100 (asumimos mil por la coma)
                    return int(float(val.replace(',', '.')) * 1000)
            
            if '.' in val:
                parts = val.split('.')
                if len(parts[-1]) == 3: # 1.200 -> 1200
                    return int(val.replace('.', ''))
                else: # 14.1 -> 14100
                    return int(float(val) * 1000)
            
            return int(val)
    except (ValueError, TypeError):
        digits = re.sub(r'[^\d]', '', val)
        return int(digits) if digits else 0

def extract_metrics_by_coordinates(img_path):
    """
    Nuevo extractor 100% exacto basado en el 'Resumen' de Meta Business Suite.
    Ya no usa RegEx general, sino que busca dónde está escrita la columna 'Visualizaciones', 
    'Espectadores' e 'Interacciones' en la pantalla, y obtiene los números que caen 
    exactamente debajo de ellas horizontalmente en la tabla.
    """
    metrics = {
        "Titulo": "Publicación de Meta",
        "Visualizaciones": "N/D",
        "Espectadores": "N/D",
        "Interacciones": "N/D"
    }
    
    try:
        img = Image.open(img_path).convert('L')
        # Utilizamos psm 6 porque es ideal para tablas, nos devuelve las coordenadas de cada bloque.
        data = pytesseract.image_to_data(img, lang='spa+eng', config='--psm 6', output_type=Output.DICT)
    except Exception as e:
        print(f"Error realizando OCR: {e}")
        return metrics

    # === 1. Localizar palabras en la imagen ===
    words = []
    for i in range(len(data['text'])):
        w_text = data['text'][i].strip()
        if w_text:
            words.append({
                "text": w_text,
                "left": data['left'][i],
                "top": data['top'][i],
                "width": data['width'][i],
                "height": data['height'][i]
            })
    
    # Ordenar por posición real
    words.sort(key=lambda x: (x["top"], x["left"]))

    # === 2. Extraer el Título (Meta - Surgical Anchor) ===
    anchor_w = None
    for w in words:
        if "publicado" in w["text"].lower():
            anchor_w = w
            break
    
    if anchor_w:
        title_candidates = []
        # Buscar arriba del anchor "Publicado"
        for w in words:
            if (anchor_w["top"] - 180) < w["top"] < (anchor_w["top"] - 5):
                # Evitar basura de la URL o UI superior
                if w["top"] > 150: 
                    title_candidates.append(w)
        
        if title_candidates:
            title_candidates.sort(key=lambda x: (x["top"] // 15, x["left"]))
            metrics["Titulo"] = " ".join([c["text"] for c in title_candidates[:15]])
    
    # Fallback si no hay anchor o quedó vacío
    if metrics["Titulo"] == "Publicación de Meta":
        potential = [w["text"] for w in words if 200 < w["top"] < 400 and len(w["text"]) > 5]
        if potential:
            metrics["Titulo"] = " ".join(potential[:10])

    # === 3. Coordenadas de Columnas Métricas ===
    headers = {
        "visualizaciones": {"rect": None, "val": "", "keywords": ["visualizaciones", "reproducciones", "vistas"]},
        "espectadores": {"rect": None, "val": "", "keywords": ["espectadores", "alcance", "público", "personas"]},
        "interacciones": {"rect": None, "val": "", "keywords": ["interacciones", "reacciones", "engagement", "clics"]}
    }
    
    for h_key, h_info in headers.items():
        for w in words:
            if any(kw in w["text"].lower() for kw in h_info["keywords"]):
                h_info["rect"] = w
                break 

    # 2. Buscar el número más cercano debajo de cada encabezado
    for h_key, h_info in headers.items():
        if h_info["rect"]:
            h_rect = h_info["rect"]
            best_val = ""
            candidates = []
            for w in words:
                # El número debe estar DEBAJO del encabezado
                # Aumentamos el rango vertical para capturar números que estén un poco más abajo
                if w["top"] > (h_rect["top"] + h_rect["height"]) and (w["top"] - h_rect["top"]) < 300:
                    # El centro X del número debe estar alineado con el encabezado
                    w_center = w["left"] + w["width"] / 2
                    h_center = h_rect["left"] + h_rect["width"] / 2
                    if abs(w_center - h_center) < (h_rect["width"] / 2 + 80):
                        # IMPORTANTE: No puede ser el mismo texto del encabezado (evitar duplicados)
                        if any(kw in w["text"] for kw in h_info["keywords"]):
                            continue
                        # Si contiene dígitos o es la palabra 'mil', es un candidato
                        if re.search(r'\d', w["text"]) or w["text"] in ["mil", "k"]:
                            candidates.append(w)
            
            # Ordenar por posición para reconstruir el número (ej: "14," "1" "mil")
            # Usamos un margen de 20px en 'top' para agrupar palabras en la misma línea
            candidates.sort(key=lambda x: (x["top"] // 20, x["left"]))
            
            val_parts = []
            seen_texts = set()
            if candidates:
                # Tomamos la primera línea de números que aparezca debajo del título
                first_row_y = candidates[0]["top"]
                for c in candidates:
                    if abs(c["top"] - first_row_y) < 50:
                        txt = c["text"]
                        if txt not in seen_texts:
                            val_parts.append(txt)
                            seen_texts.add(txt)
                
                best_val = " ".join(val_parts)
                # Si el número parece decimal pero le falta el 'mil'
                if best_val and not any(m in best_val.lower() for m in ["mil", "k"]):
                    if "," in best_val or "." in best_val:
                        best_val += " mil"
            
            h_info["val"] = best_val.strip()

    # 3. Limpiar y asignar
    for k in metrics.keys():
        if k == "Titulo": continue
        v = headers[k.lower()]["val"]
        if v:
            # Dejar números, puntos, comas y multiplicadores
            cleaned_v = re.sub(r'[^\d.,kKmil]', '', v)
            # Limpieza final de duplicados como "milmil"
            cleaned_v = cleaned_v.replace('milmil', 'mil')
            if cleaned_v: metrics[k] = cleaned_v

    return metrics

def analizar_publico(path_csv):
    """
    Lee un archivo CSV exportado desde Meta y estructura la demografía del público.
    - Filtra Paises exclusivamente al Continente Americano.
    - Captura Top Ciudades, Edades y Género.
    """
    if not os.path.exists(path_csv):
        return None

    # Países del Continente Americano permitidos
    paises_america = [
        "México", "Estados Unidos", "Canadá", "Guatemala", "Belice", "El Salvador", 
        "Honduras", "Nicaragua", "Costa Rica", "Panamá", "Colombia", "Venezuela", 
        "Ecuador", "Perú", "Bolivia", "Chile", "Argentina", "Uruguay", "Paraguay", 
        "Brasil", "Cuba", "República Dominicana", "Haití", "Puerto Rico", "Jamaica"
    ]
    
    datos = {
        "ciudades": [],
        "edades": {"Hombres": {}, "Mujeres": {}},
        "paises": []
    }
    
    try:
        # Los CSV de Meta usualmente vienen en formato UTF-16LE
        with open(path_csv, encoding='utf-16le', errors='ignore') as f:
            reader = list(csv.reader(f, delimiter=','))
            
            # 1. Ciudades
            try:
                idx = next(i for i, row in enumerate(reader) if row and 'Principales ciudades' in str(row[0]))
                ciudades_nombres = reader[idx + 1]
                ciudades_valores = reader[idx + 2]
                for i, ciudad in enumerate(ciudades_nombres):
                    if ciudad.strip() and i < len(ciudades_valores):
                        if len(datos["ciudades"]) < 5: # Solo Top 5 para evitar recargar diseño
                            c_name = ciudad.split(',')[0].strip()
                            datos["ciudades"].append({"nombre": c_name, "valor": float(ciudades_valores[i] or 0)})
            except (StopIteration, IndexError, ValueError):
                pass
                
            # 2. Edad y Sexo
            try:
                idx = next(i for i, row in enumerate(reader) if row and 'Edad y sexo' in str(row[0]))
                row_idx = idx + 2
                while row_idx < len(reader) and reader[row_idx] and reader[row_idx][0].strip():
                    rango = reader[row_idx][0].strip()
                    h_val = float(reader[row_idx][1]) if len(reader[row_idx]) > 1 and reader[row_idx][1] else 0
                    m_val = float(reader[row_idx][2]) if len(reader[row_idx]) > 2 and reader[row_idx][2] else 0
                    if h_val > 0 or m_val > 0:
                        datos["edades"]["Hombres"][rango] = h_val
                        datos["edades"]["Mujeres"][rango] = m_val
                    row_idx += 1
            except (StopIteration, IndexError, ValueError):
                pass
                
            # 3. Países Americanos
            try:
                idx = next(i for i, row in enumerate(reader) if row and 'Principales países' in str(row[0]))
                paises_nombres = reader[idx + 1]
                paises_valores = reader[idx + 2]
                for i, pais in enumerate(paises_nombres):
                    pais_limpio = pais.strip()
                    if pais_limpio and i < len(paises_valores):
                        # Validación de Filtro Continente
                        if any(am.lower() == pais_limpio.lower() for am in paises_america):
                            datos["paises"].append({"nombre": pais_limpio, "valor": float(paises_valores[i] or 0)})
                # Ordenar por valor (Top) y cortar
                datos["paises"] = sorted(datos["paises"], key=lambda x: x["valor"], reverse=True)[:5]
            except (StopIteration, IndexError, ValueError):
                pass
                
        return datos if any([datos["ciudades"], datos["paises"], datos["edades"]["Hombres"]]) else None
        
    except Exception as e:
        print(f"Error parseando CSV (Demográfico): {e}")
        return None

def image_to_base64(img_path):
    """Convierte la imagen en Base64 con compresión y redimensionado para reducir el peso del HTML"""
    try:
        with Image.open(img_path) as img:
            # Convertir a RGB si es necesario (JPEG no soporta transparencia/alfa)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Redimensionar si es muy grande (máximo 1200px de ancho)
            MAX_WIDTH = 1200
            if img.width > MAX_WIDTH:
                w_percent = (MAX_WIDTH / float(img.width))
                h_size = int((float(img.height) * float(w_percent)))
                img = img.resize((MAX_WIDTH, h_size), Image.Resampling.LANCZOS)
            
            # Guardar en un buffer de memoria con compresión JPEG (Calidad 70)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=70, optimize=True)
            encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Error comprimiendo imagen {img_path}: {e}")
        # Intento de fallback si PIL falla
        try:
            with open(img_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                ext = os.path.splitext(img_path)[1].lower()
                mime_type = "image/png" if ext == ".png" else "image/jpeg"
                return f"data:{mime_type};base64,{encoded_string}"
        except:
            return ""

def process_folder_and_generate_report(folder_path, folder_name, base_dir, cliente_formal=None, periodo=None, lugar=None):
    """
    Lee capturas, las analiza mapeando estrictamente las columnas, incorpora datos CSV
    crea un TOP 3 de impacto y genera los reportes HTML independientes.
    """
    cliente = cliente_formal if cliente_formal else os.path.basename(folder_name)
    periodo_uso = periodo if periodo else PERIODO
    lugar_uso = lugar if lugar else LUGAR
    
    # Guardar en la carpeta "reportes" en la raíz del sitio web, organizado por mes
    website_root = os.path.dirname(base_dir)
    mes_subfolder = periodo_uso.split(' ')[0] if periodo_uso else "General"
    reportes_dir = os.path.join(website_root, "reportes", mes_subfolder)
    
    if not os.path.exists(reportes_dir):
        os.makedirs(reportes_dir)

    print(f"\n--- Iniciando creación de reporte para: {cliente} ---")
    
    # Cargar información extra del cliente (Entidad, Dirigido a)
    info_cliente = {}
    try:
        with open(os.path.join(base_dir, "clientes_info.json"), 'r', encoding='utf-8') as f:
            clientes_data = json.load(f)
            info_cliente = clientes_data.get(cliente, {})
    except Exception as e:
        print(f"[Aviso] No se pudo cargar clientes_info.json o no existe el cliente: {e}")
    
    # Intentar cargar CSV público
    ruta_csv = os.path.join(base_dir, "Datos", "publico_intlax_marzo_2026.csv")
    datos_publico = analizar_publico(ruta_csv)
    if datos_publico:
        print("[Datos] Se ha detectado e integrado el anexo CSV demográfico filtrado por Continente Americano.")
    
    valid_exts = ('.jpg', '.jpeg', '.png')
    report_data_meta = []
    report_data_tiktok = []
    all_posts = []

    sum_visualizaciones = 0
    sum_espectadores = 0
    sum_interacciones = 0

    plataformas = ["Meta", "TikTok"]
    
    for plat in plataformas:
        plat_dir = os.path.join(folder_path, plat)
        if not os.path.exists(plat_dir):
            continue
            
        for filename in os.listdir(plat_dir):
            if filename.lower().endswith(valid_exts) and not filename.startswith('.'):
                img_path = os.path.abspath(os.path.join(plat_dir, filename))
                print(f"[{folder_name} - {plat}] Leyendo coordenadas en: {filename}...")
                
                try:
                    is_tiktok = (plat == "TikTok")
                    if is_tiktok:
                        metrics = extract_tiktok_metrics(img_path)
                    else:
                        metrics = extract_metrics_by_coordinates(img_path)
                    
                    v_calc = parse_metric_to_int(metrics['Visualizaciones'])
                    v_esp = parse_metric_to_int(metrics['Espectadores'])
                    v_int = parse_metric_to_int(metrics['Interacciones'])
                    
                    # --- CONSISTENCY CHECK ---
                    # 1. El Alcance (Espectadores) no puede ser mayor que las Impresiones (Visualizaciones)
                    if not is_tiktok and v_esp > v_calc and v_calc > 0:
                        if v_esp > v_calc * 5: v_esp = v_esp // 10
                        if v_esp > v_calc: v_esp = v_calc
                    
                    # 2. Las Visualizaciones no suelen ser 10 veces mayores que el Alcance (Ratio Check)
                    # Si Vis > Esp * 8, es muy probable que el OCR leyó "57,1 mil" como "571 mil" (error 10x)
                    if not is_tiktok and v_esp > 0 and v_calc > v_esp * 8:
                        # Corregir el 10x de visualizaciones si el ratio es absurdo
                        v_calc = v_calc // 10
                    
                    print(f"   [OCR DEBUG] {filename} -> Vis: {v_calc} | Esp: {v_esp} | Int: {v_int} | (Original: V={metrics['Visualizaciones']}, E={metrics['Espectadores']})")
                    
                    sum_visualizaciones += v_calc
                    sum_espectadores += v_esp
                    sum_interacciones += v_int
                    
                    base64_img_data = image_to_base64(img_path)
                    
                    post_data = {
                        "filename": filename,
                        "relative_img_path": base64_img_data,
                        "metrics": {
                            "Titulo": metrics.get("Titulo", "Publicación"),
                            "Visualizaciones": format_number(v_calc),
                            "Espectadores": format_number(v_esp),
                            "Interacciones": format_number(v_int)
                        },
                        "_orden_visualizaciones": v_calc,
                        "_display_vis": format_number(v_calc),
                        "_display_esp": format_number(v_esp),
                        "_display_int": format_number(v_int)
                    }
                    
                    all_posts.append(post_data)
                    
                    if is_tiktok:
                        report_data_tiktok.append(post_data)
                    else:
                        report_data_meta.append(post_data)
                    
                except Exception as e:
                    print(f"Error procesando imagen {filename}: {e}")

    # Extraer el Top 3 por Visualizaciones combinando todo
    top_posts = sorted(all_posts, key=lambda x: x["_orden_visualizaciones"], reverse=True)[:3]

    # Helper function para Jinja ya que de forma nativa a veces jinja2 requiere emular enumerate()
    def enumerate_top(lista):
        # Devuelve (1, list[0]), (2, list[1]), (3, list[2])
        return [(i+1, v) for i, v in enumerate(lista)]

    # === Logica Comparativa MoM ===
    data_list = []
    testigos_dir = os.path.dirname(os.path.dirname(folder_path)) if "Testigos" in folder_path else os.path.join(base_dir, "Testigos")
    
    if os.path.exists(testigos_dir):
        for periodo_folder in os.listdir(testigos_dir):
            periodo_path = os.path.join(testigos_dir, periodo_folder)
            if os.path.isdir(periodo_path):
                cliente_path = os.path.join(periodo_path, cliente)
                metrics_file = os.path.join(cliente_path, "metrics.json")
                if os.path.exists(metrics_file):
                    try:
                        with open(metrics_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            sort_key = parse_periodo(data.get("periodo", ""))
                            data["_sort"] = sort_key
                            data_list.append(data)
                    except Exception:
                        pass
    
    # Agregar datos actuales a la lista
    current_data = {
        "periodo": periodo_uso,
        "visualizaciones": sum_visualizaciones,
        "espectadores": sum_espectadores,
        "interacciones": sum_interacciones,
        "_sort": parse_periodo(periodo_uso)
    }
    
    # Reemplazar el actual si ya existe en la lista histórica (por si se re-ejecuta)
    data_list = [d for d in data_list if d["periodo"] != periodo_uso]
    data_list.append(current_data)
    data_list = sorted(data_list, key=lambda x: x["_sort"])
    
    has_comparativo = False
    diff_vis = diff_esp = diff_int = 0
    d_vis_cls = d_vis_icn = d_esp_cls = d_esp_icn = d_int_cls = d_int_icn = ""
    prev_period_name = ""
    previous = {}
    
    current_idx = next((i for i, d in enumerate(data_list) if d["periodo"] == periodo_uso), -1)
    if current_idx > 0:
        has_comparativo = True
        previous = data_list[current_idx - 1]
        prev_period_name = previous.get("periodo", "")
        
        diff_vis = calculate_mom(current_data["visualizaciones"], previous.get("visualizaciones", 0))
        diff_esp = calculate_mom(current_data["espectadores"], previous.get("espectadores", 0))
        diff_int = calculate_mom(current_data["interacciones"], previous.get("interacciones", 0))
        
        d_vis_cls, d_vis_icn = get_diff_ui(diff_vis)
        d_esp_cls, d_esp_icn = get_diff_ui(diff_esp)
        d_int_cls, d_int_icn = get_diff_ui(diff_int)
    # === Fin Logica Comparativa ===

    template = Template(HTML_TEMPLATE)
    html_output = template.render(
        cliente=cliente,
        periodo=periodo_uso,
        plataforma=PLATAFORMA,
        lugar=lugar_uso,
        reportes_data_meta=report_data_meta,
        reportes_data_tiktok=report_data_tiktok,
        top_posts=top_posts,
        datos_publico=datos_publico,
        info_cliente=info_cliente,
        enumerate_top=enumerate_top,
        total_visualizaciones=format_number(sum_visualizaciones),
        total_espectadores=format_number(sum_espectadores),
        total_interacciones=format_number(sum_interacciones),
        has_comparativo=has_comparativo,
        prev_period_name=prev_period_name,
        diff_vis=f"{diff_vis:.1f}", d_vis_cls=d_vis_cls, d_vis_icn=d_vis_icn,
        diff_esp=f"{diff_esp:.1f}", d_esp_cls=d_esp_cls, d_esp_icn=d_esp_icn,
        diff_int=f"{diff_int:.1f}", d_int_cls=d_int_cls, d_int_icn=d_int_icn,
        prev_vis=previous.get("visualizaciones", 0), curr_vis=sum_visualizaciones,
        prev_esp=previous.get("espectadores", 0), curr_esp=sum_espectadores,
        prev_int=previous.get("interacciones", 0), curr_int=sum_interacciones,
        prev_period_short=prev_period_name.split(' ')[0],
        curr_period_short=periodo_uso.split(' ')[0]
    )

    report_filename = f"Reporte_{cliente.replace(' ', '_')}_{periodo_uso.replace(' ', '_')}.html"
    report_path = os.path.join(reportes_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
        
    metrics_export_path = os.path.join(folder_path, "metrics.json")
    metrics_data = {
        "cliente": cliente,
        "periodo": periodo_uso,
        "total_posts": len(all_posts),
        "visualizaciones": sum_visualizaciones,
        "espectadores": sum_espectadores,
        "interacciones": sum_interacciones
    }
    try:
        with open(metrics_export_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error guardando metrics.json en {folder_path}: {e}")
        
    print(f"✅ Reporte generado y guardado en: {report_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generador de reportes ALFA")
    parser.add_argument('--folder', type=str, help='Nombre de la carpeta específica (ej. client_5)')
    parser.add_argument('--cliente', type=str, help='Nombre formal del cliente')
    parser.add_argument('--periodo', type=str, help='El mes y año (ej. Abril 2026)')
    parser.add_argument('--lugar', type=str, help='Ciudad y estado')
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.folder:
        # Modo Dinámico Específico
        ruta_directa = os.path.join(base_dir, "Testigos", args.folder)
        if not os.path.exists(ruta_directa):
            print(f"Error: No se encontró la carpeta {ruta_directa}")
            return
        
        process_folder_and_generate_report(ruta_directa, args.folder, base_dir, args.cliente, args.periodo, args.lugar)
    else:
        print("Uso en solitario deshabilitado sin parámetros. Use --folder client_id desde PHP.")

if __name__ == "__main__":
    main()
