import os
import re
import csv
import base64
import pytesseract
from PIL import Image
from pytesseract import Output
from jinja2 import Template

# Configuración de Tesseract para macOS (Homebrew en M1/M2 o Intel)
if os.path.exists('/opt/homebrew/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
elif os.path.exists('/usr/local/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# Mapeo de carpetas a nombres formales de clientes
CLIENTES_MAP = {
    "Ana Lilia rivera": "Ana Lilia Rivera",
    "Ruben becerra": "Rubén Becerra Cerón",
    "Benito Juarez o Ruben Becerra": "Rubén Becerra Cerón",
    "Calpulalpan": "Gobierno Municipal De Calpulalpan, Tlaxcala"
}

# Configuración del reporte
PERIODO = "Marzo 2026"
PLATAFORMA = "Facebook"
LUGAR = "Calpulalpan, Tlaxcala"

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

        /* --- ANEXOS TESTIGOS --- */
        .anexos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; }

        .card {
            background-color: var(--bg-surface);
            border-radius: 12px; overflow: hidden;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.6); border-color: var(--accent); }

        .card-img-wrapper {
            width: 100%; height: 300px;
            background-color: #050505;
            display: flex; align-items: center; justify-content: center;
            border-bottom: 1px solid var(--border-color); padding: 5px;
        }
        .card img { max-width: 100%; max-height: 100%; object-fit: contain; }

        .metrics-container { padding: 20px; background-color: var(--bg-card); }
        .metric-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px dashed var(--border-color); }
        .metric-row:last-child { border-bottom: none; }
        .metric-label { font-size: 1rem; color: var(--text-secondary); font-weight: 500; }
        .metric-value { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
        .filename-caption { font-size: 0.75rem; color: #52525b; text-align: center; margin-top: 15px; word-wrap: break-word; }
        .post-title-extract { font-size: 0.85rem; color: var(--text-primary); font-weight: 600; font-style: italic; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px dashed var(--border-color); line-height: 1.4; }

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
            :root {
                --bg-base: #ffffff;
                --bg-surface: #ffffff;
                --bg-card: #f8fafc;
                --text-primary: #000000;
                --text-secondary: #333333;
                --accent: #ca8a04; /* Oro oscuro para papel blanco */
                --border-color: #cccccc;
            }
            body { background-color: #ffffff !important; color: #000000 !important; font-size: 10pt; }
            .content-wrap { padding: 0 !important; }
            .container { max-width: 100% !important; padding: 0 !important; margin: 0 !important; }
            .print-btn { display: none !important; }
            
            /* Portada Ligera */
            header { background: #fff !important; box-shadow: none !important; border: 1px solid #ddd !important; padding: 20px !important; margin-bottom: 15px !important; }
            header::before { background: var(--accent) !important; height: 6px !important; }
            .main-title { font-size: 20pt !important; color: #000 !important; margin-bottom: 10px !important; }
            .subtitle { font-size: 14pt !important; color: #444 !important; }
            .details-badge { background: #f0f0f0 !important; border: 1px solid #ccc !important; padding: 5px 10px !important; }
            .details-badge span, .details-badge strong { color: #000 !important; }

            /* Secciones Interiores */
            .section-box { background: #fff !important; border: 1px solid #ddd !important; padding: 15px !important; margin-bottom: 15px !important; page-break-inside: avoid; }
            h2.section-title { font-size: 14pt !important; border-bottom: 2px solid #eee !important; color: #000 !important; margin-bottom: 15px !important; padding-bottom: 5px !important; }
            
            /* Cajas de resumen numérico sin fondos oscuros */
            .summary-card { background: #fefefe !important; border: 1px solid #ddd !important; box-shadow: none !important; padding: 10px !important; }
            .summary-card .value { color: #000 !important; font-size: 16pt !important; }
            .summary-card .label { color: #222 !important; }
            
            /* Anexos: Multi-columna, fotos miniatura, sin cajas oscuras */
            .anexos-grid { display: grid !important; grid-template-columns: repeat(4, 1fr) !important; gap: 10px !important; }
            .anexos-grid .card { background: #fff !important; border: 1px solid #ddd !important; box-shadow: none !important; margin-bottom: 0 !important; page-break-inside: avoid; }
            .card-img-wrapper { background: #fff !important; height: 120px !important; padding: 2px !important; border-bottom: 1px solid #eee !important; }
            .metrics-container { background: #fafafa !important; padding: 10px !important; }
            .metric-row { border-bottom: 1px dotted #ccc !important; padding: 4px 0 !important; }
            .metric-label { color: #333 !important; font-size: 8pt !important; }
            .metric-value { color: #000 !important; font-size: 9pt !important; }
            .post-title-extract { color: #000 !important; font-size: 8pt !important; border-bottom: 1px solid #ccc !important; padding-bottom: 5px !important; margin-bottom: 5px !important; }
            
            /* El Podio: colores de bordes reajustados para papel */
            .card[style*="border: 2px solid var(--accent)"], .card[style*="border: 2px solid #FFD700"] { border: 2px solid var(--accent) !important; }
            .card[style*="border: 2px solid #94a3b8"], .card[style*="border: 2px solid #C0C0C0"] { border: 2px solid #666 !important; }
            .card[style*="border: 2px solid #b45309"], .card[style*="border: 2px solid #CD7F32"] { border: 2px solid #b45309 !important; }

            /* Demografía adaptada a hoja blanca */
            .section-box > div[style*="grid-template-columns"] { display: grid !important; grid-template-columns: repeat(3, 1fr) !important; gap: 15px !important; }
            .section-box > div > div { background: #fff !important; border: 1px solid #ddd !important; box-shadow: none !important; }
            .section-box > div > div h4 { color: #000 !important; font-size: 10pt !important; }
            
            /* Footer impreso en Blanco para no gastar cartucho negro, ni ocupar mucho espacio */
            footer { background: #fff !important; border-top: 2px solid #000 !important; padding: 15px 0 10px !important; margin-top: 15px !important; }
            .footer-grid { display: grid !important; grid-template-columns: repeat(3, 1fr) !important; gap: 15px !important; margin-bottom: 10px !important; }
            .footer-col h4, .footer-col p, .footer-col a, .footer-col span { color: #000 !important; }
            .footer-col h4 { border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 10px; font-size: 10pt !important; }
            .footer-col ul li { line-height: 1.2 !important; margin-bottom: 5px !important; font-size: 8pt !important; }
            .container > p { color: #555 !important; border-top: none !important; margin-top: 0 !important; padding-top: 0 !important; }
            .text-accent, .text-yellow { color: var(--accent) !important; }
        }
    </style>
</head>
<body>

<div class="container content-wrap">
    <!-- PORTADA -->
    <header>
        <span class="intlax-branding"><span class="text-accent">IN</span>TLAX.CLAUD</span>
        <h1 class="main-title">Reporte Ejecutivo de Desempeño</h1>
        <h2 class="subtitle">{{ cliente }}</h2>
        
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

    <!-- TOP 3 PODIO PUBLICACIONES -->
    {% if top_posts and top_posts|length > 0 %}
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-award fa-yellow"></i> Top 3 Contenidos Destacados</h2>
        <div class="anexos-grid" style="grid-template-columns: repeat(3, 1fr);">
            {% for idx, item in enumerate_top(top_posts) %}
            <div class="card" style="border: {% if idx == 1 %}2px solid var(--accent){% elif idx == 2 %}2px solid #C0C0C0{% else %}2px solid #CD7F32{% endif %}; position: relative;">
                
                <div style="position: absolute; top: 0; right: 0; padding: 3px 10px; border-bottom-left-radius: 6px; font-weight: bold; font-size: 0.75rem; background: {% if idx == 1 %}var(--accent); color: #000{% elif idx == 2 %}#C0C0C0; color: #000{% else %}#CD7F32; color: #fff{% endif %}; z-index: 10;">
                    Rango #{{ idx }}
                </div>

                <div class="card-img-wrapper">
                    <img src="{{ item.relative_img_path }}" alt="Testigo fotográfico {{ idx }}">
                </div>
                <div class="metrics-container" style="background-color: var(--bg-card);">
                    <div class="post-title-extract">"{{ item.metrics.get('Titulo', '') }}"</div>
                    <div class="metric-row">
                        <span class="metric-label" style="font-weight:700;"><i class="fas fa-eye fa-yellow"></i> Visualizaciones</span>
                        <span class="metric-value">{{ item.metrics['Visualizaciones'] }}</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- MÉTRICAS DE AUDIENCIA CSV -->
    {% if datos_publico %}
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-users fa-yellow"></i> Demografía y Alcance Geográfico</h2>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
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

    <!-- GLOSARIO DE TÉRMINOS -->
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-book fa-yellow"></i> Glosario de Plataforma</h2>
        <ul class="glossary-list">
            <li><strong>Visualizaciones:</strong> Veces que la publicación apareció en la pantalla de un seguidor.</li>
            <li><strong>Espectadores:</strong> Cantidad de personas únicas reales comprobadas por el visor de Meta.</li>
            <li><strong>Interacciones:</strong> Total de clics, likes o comentarios generados durante el periodo activo.</li>
        </ul>
    </div>

    <!-- ANEXOS TESTIGOS -->
    <div class="section-box" style="margin-bottom: 0;">
        <h2 class="section-title"><i class="fas fa-camera fa-yellow"></i> Expediente Fotográfico de Evidencias</h2>
        {% if reportes_data %}
        <div class="anexos-grid">
            {% for item in reportes_data %}
            <div class="card">
                <div class="card-img-wrapper">
                    <img src="{{ item.relative_img_path }}" alt="Testigo fotográfico">
                </div>
                <div class="metrics-container">
                    <div class="post-title-extract">"{{ item.metrics.get('Titulo', '') }}"</div>
                    <div class="metric-row">
                        <span class="metric-label">Visualizaciones</span>
                        <span class="metric-value">{{ item.metrics['Visualizaciones'] }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Espectadores</span>
                        <span class="metric-value">{{ item.metrics['Espectadores'] }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Interacci.</span>
                        <span class="metric-value">{{ item.metrics['Interacciones'] }}</span>
                    </div>
                    <div class="filename-caption">{{ item.filename }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
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

def parse_metric_to_int(val_str):
    """ Convierte cadenas como '1.5k', '5 mil', '1,200' a enteros matemáticos. """
    if not val_str or val_str == "N/D":
        return 0
    val = val_str.lower().replace(',', '')
    try:
        if 'k' in val or 'mil' in val:
            v_clean = val.replace('k', '').replace('mil', '').strip()
            return int(float(v_clean) * 1000)
        return int(float(val))
    except (ValueError, TypeError):
        return 0

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

    # === 1. Extraer el Título (Parte superior izquierda) ===
    # Juntamos texto válido hasta topar con UI de Facebook o rebasar 70 caracteres
    valid_words = []
    for i, texto in enumerate(data['text']):
        w_clean = texto.strip('.:,-_@OQ0)(\|][{}<>\'\"')
        if w_clean:
            valid_words.append({
                "text": texto,
                "top": data['top'][i],
                "left": data['left'][i]
            })
            
    # Ordenar estrictamente de arriba hacia abajo (top) para leer secuencialmente el header
    valid_words.sort(key=lambda x: x['top'])
    
    titulo_extracto = []
    for w in valid_words:
        txt = w['text']
        txt_l = txt.lower().strip()
        
        # Palabras reservadas de la App que nos indican que YA SALIMOS del Título de la Foto
        if txt_l in ['publicación', 'resumen', 'vista', 'previa', 'publicado', 'promocionar', 'interacciones', 'visualizaciones', 'feed', 'editar']:
            break
            
        # Filtro de basura OCR
        if len(txt) <= 2 and not txt.isupper() and not txt.isalnum():
            continue
            
        titulo_extracto.append(txt)
        
        # Limite estético visual (dar una idea sin robar espacio)
        if len(" ".join(titulo_extracto)) > 70:
            titulo_extracto.append("...")
            break
            
    if titulo_extracto:
        metrics["Titulo"] = " ".join(titulo_extracto).strip()

    # === 2. Coordenadas de Columnas Métricas ===
    headers = {
        "visualizaciones": {"rect": None, "val": ""},
        "espectadores": {"rect": None, "val": ""},
        "interacciones": {"rect": None, "val": ""}
    }
    
    baseline_y = -1
    
    # 1. Definir los límites X horizontales de las columnas
    for i, word in enumerate(data['text']):
        w_lower = word.lower().strip('.:,O@Q0) ')
        if not w_lower: continue
        
        for h_key in headers.keys():
            if h_key in w_lower and headers[h_key]["rect"] is None:
                # Si encontramos el encabezado, guardamos sus coordenadas X e Y
                headers[h_key]["rect"] = {
                    "left": data['left'][i],
                    "right": data['left'][i] + data['width'][i]
                }
                
                # Registramos en qué piso Y están estos encabezados
                if baseline_y == -1 or data['top'][i] < baseline_y + 30:
                    baseline_y = data['top'][i]

    # 2. Escanear todo lo que está más abajo de los encabezados (fila de resultados)
    for i, word in enumerate(data['text']):
        raw_word = word.strip().replace('O', '0').replace(')', '').replace('_', '')
        if not raw_word or not re.search(r'\d', raw_word):
            continue
            
        w_top = data['top'][i]
        w_left = data['left'][i]
        w_right = w_left + data['width'][i]
        
        # Tiene que estar en el renglón de abajo del título (baseline_y), 
        # pero no tan abajo como para saltar a otra sección
        if baseline_y != -1 and w_top > baseline_y and (w_top - baseline_y) < 180:
            
            # Revisar en cuál de las zapatas de nuestras columnas cae
            for h_key, h_data in headers.items():
                if h_data["rect"]:
                    # Margen de holgura por si el número está centrado o muy pegado
                    h_left = h_data["rect"]["left"] - 45
                    h_right = h_data["rect"]["right"] + 45
                    
                    if w_left >= h_left and w_right <= h_right:
                        # Acumulamos el texto (Meta a veces divide "16.704" en "1", "6.", "704")
                        h_data["val"] += raw_word

    # 3. Limpiar valores acumulados matemáticamente exactos
    for k in metrics.keys():
        if k == "Titulo":
            continue
        v = headers[k.lower()]["val"]
        if v:
            # Eliminamos basura y dejamos solo números e indicadores de miles si los hubiera
            cleaned_v = re.sub(r'[^\d.,kKmil]', '', v)
            if cleaned_v:
                metrics[k] = cleaned_v

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
    """Convierte la imagen original en Base64 para incrustarla dentro del HTML"""
    try:
        with open(img_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            ext = os.path.splitext(img_path)[1].lower()
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Error convirtiendo imagen a base64: {e}")
        return ""

def process_folder_and_generate_report(folder_path, folder_name, base_dir):
    """
    Lee capturas, las analiza mapeando estrictamente las columnas, incorpora datos CSV
    crea un TOP 3 de impacto y genera los reportes HTML independientes.
    """
    cliente = CLIENTES_MAP.get(folder_name, folder_name)
    
    # Guardar en la carpeta "reportes" en la raíz del sitio web, un nivel arriba
    website_root = os.path.dirname(base_dir)
    reportes_dir = os.path.join(website_root, "reportes")
    
    if not os.path.exists(reportes_dir):
        os.makedirs(reportes_dir)

    print(f"\n--- Iniciando creación de reporte para: {cliente} ---")
    
    # Intentar cargar CSV público
    ruta_csv = os.path.join(base_dir, "Datos", "publico_intlax_marzo_2026.csv")
    datos_publico = analizar_publico(ruta_csv)
    if datos_publico:
        print("[Datos] Se ha detectado e integrado el anexo CSV demográfico filtrado por Continente Americano.")
    
    valid_exts = ('.jpg', '.jpeg', '.png')
    report_data = []

    sum_visualizaciones = 0
    sum_espectadores = 0
    sum_interacciones = 0

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(valid_exts) and not filename.startswith('.'):
            img_path = os.path.abspath(os.path.join(folder_path, filename))
            print(f"[{folder_name}] Leyendo coordenadas en: {filename}...")
            
            try:
                metrics = extract_metrics_by_coordinates(img_path)
                
                v_calc = parse_metric_to_int(metrics['Visualizaciones'])
                sum_visualizaciones += v_calc
                sum_espectadores += parse_metric_to_int(metrics['Espectadores'])
                sum_interacciones += parse_metric_to_int(metrics['Interacciones'])
                
                base64_img_data = image_to_base64(img_path)
                
                report_data.append({
                    "filename": filename,
                    "relative_img_path": base64_img_data,
                    "metrics": metrics,
                    "_orden_visualizaciones": v_calc # Usado internamente para el TOP 3
                })
                
            except Exception as e:
                print(f"Error procesando imagen {filename}: {e}")

    # Extraer el Top 3 por Visualizaciones (Orden Numérico Descendente)
    top_posts = sorted(report_data, key=lambda x: x["_orden_visualizaciones"], reverse=True)[:3]

    # Helper function para Jinja ya que de forma nativa a veces jinja2 requiere emular enumerate()
    def enumerate_top(lista):
        # Devuelve (1, list[0]), (2, list[1]), (3, list[2])
        return [(i+1, v) for i, v in enumerate(lista)]

    template = Template(HTML_TEMPLATE)
    html_output = template.render(
        cliente=cliente,
        periodo=PERIODO,
        plataforma=PLATAFORMA,
        lugar=LUGAR,
        reportes_data=report_data,
        top_posts=top_posts,
        datos_publico=datos_publico,
        enumerate_top=enumerate_top,
        total_visualizaciones=format_number(sum_visualizaciones),
        total_espectadores=format_number(sum_espectadores),
        total_interacciones=format_number(sum_interacciones)
    )

    report_filename = f"Reporte_{folder_name.replace(' ', '_').replace('o_Ruben', '')}_{PERIODO.replace(' ', '_')}.html"
    report_path = os.path.join(reportes_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
        
    print(f"✅ Reporte generado y guardado en: {report_path}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Busca las carpetas objetivo en la raíz o dentro de "Testigos"
    possible_roots = [base_dir, os.path.join(base_dir, "Testigos")]
    
    # Nombres de carpeta estrictos (para mantener la compatibilidad pedida)
    folders_to_scan = list(CLIENTES_MAP.keys())
    
    # Agregar carpetas capitalizadas al mapeo si las encuentra en Testigos/
    for root in possible_roots:
        if os.path.exists(root):
            for potential_dir in os.listdir(root):
                if potential_dir.lower() in [k.lower() for k in CLIENTES_MAP.keys()]:
                    # Mapear variaciones de mayúsculas/minúsculas para no perderlas
                    real_key = next(k for k in CLIENTES_MAP.keys() if k.lower() == potential_dir.lower())
                    CLIENTES_MAP[potential_dir] = CLIENTES_MAP[real_key]
                    if potential_dir not in folders_to_scan:
                        folders_to_scan.append(potential_dir)
    
    processed_count = 0
    for root in possible_roots:
        for folder_name in folders_to_scan:
            target_folder = os.path.join(root, folder_name)
            if os.path.exists(target_folder) and os.path.isdir(target_folder):
                process_folder_and_generate_report(target_folder, folder_name, base_dir)
                processed_count += 1
                
    if processed_count == 0:
        print("\n[!] No se encontraron las carpetas específicas de los clientes.")

if __name__ == "__main__":
    main()
