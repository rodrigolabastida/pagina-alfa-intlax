import os
import json
import argparse
from jinja2 import Template

# Mapeo para ordenar meses cronológicamente
MESES_MAP = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

HTML_COMPARATIVO_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Comparativo Histórico - {{ cliente }}</title>
    <meta name="robots" content="noindex, nofollow">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #0a0a0a;
            --bg-surface: #171717;
            --bg-card: #222222;
            --text-primary: #ededed;
            --text-secondary: #a1a1aa;
            --accent: #FFD700;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --border-color: #3f3f46;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .content-wrap { padding: 40px 0; }

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
        .intlax-branding { font-family: 'Montserrat', sans-serif; font-size: 1rem; letter-spacing: 2px; font-weight: 900; margin-bottom: 15px; display: block; }
        .intlax-branding span { color: var(--accent); }
        .main-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 15px; }
        .subtitle { font-size: 1.8rem; font-weight: 400; color: var(--text-secondary); margin-bottom: 30px; }

        .section-box {
            background-color: var(--bg-surface);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 40px;
            border: 1px solid var(--border-color);
        }
        .section-title {
            font-size: 1.5rem;
            color: var(--text-primary);
            margin-bottom: 25px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }
        .fa-yellow { color: var(--accent); }

        .mom-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .mom-card {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
        }
        .mom-label { font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 10px; }
        .mom-value { font-size: 2rem; font-weight: 700; margin-bottom: 5px; }
        .mom-diff { font-size: 1.1rem; font-weight: 600; }
        .positive { color: var(--accent-green); }
        .negative { color: var(--accent-red); }
        .neutral { color: var(--text-secondary); }

        .chart-container {
            position: relative;
            height: 400px;
            width: 100%;
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }
        
        /* --- TABLA MODERNA --- */
        .table-container {
            overflow-x: auto;
            margin-top: 20px;
        }
        .modern-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
        }
        .modern-table th {
            background-color: #2a2a2a;
            color: var(--accent);
            text-align: left;
            padding: 15px 20px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
            border-bottom: 2px solid var(--border-color);
        }
        .modern-table td {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
            font-size: 0.95rem;
        }
        .modern-table tr:last-child td { border-bottom: none; }
        .modern-table tr:hover { background-color: rgba(255, 255, 255, 0.03); transition: background 0.2s; }
        
        .growth-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .badge-positive { background-color: rgba(16, 185, 129, 0.1); color: var(--accent-green); }
        .badge-negative { background-color: rgba(239, 68, 68, 0.1); color: var(--accent-red); }
        .badge-neutral { background-color: rgba(161, 161, 170, 0.1); color: var(--text-secondary); }

        .print-btn {
            background-color: var(--accent); color: #000; border: none;
            padding: 12px 25px; font-size: 1rem; font-weight: 600;
            border-radius: 30px; cursor: pointer; transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
            margin-bottom: 20px;
        }
        .print-btn:hover { background-color: #e6c200; transform: translateY(-2px); }

        /* Estilos de impresión */
        @media print {
            body { background-color: #fff !important; color: #000 !important; }
            header, .section-box, .mom-card, .chart-container, .modern-table { background-color: #fff !important; border: 1px solid #ddd !important; box-shadow: none !important; }
            .intlax-branding, .main-title, .section-title, .mom-value, .modern-table th { color: #000 !important; }
            .subtitle, .mom-label, .modern-table td { color: #333 !important; }
            .print-btn { display: none !important; }
            canvas { min-height: 100%; max-width: 100%; max-height: 100%; height: auto!important;}
        }
    </style>
</head>
<body>

<div class="container content-wrap">
    <header>
        <span class="intlax-branding"><span style="color:#FFD700">IN</span>TLAX.CLAUD</span>
        <h1 class="main-title">Reporte Comparativo Histórico</h1>
        <h2 class="subtitle">{{ cliente }}</h2>
        
        <button class="print-btn" onclick="window.print()">
            <i class="fas fa-file-pdf"></i> Imprimir / Guardar PDF
        </button>
    </header>

    {% if data|length > 1 %}
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-rocket fa-yellow"></i> Crecimiento (Último mes vs. Anterior)</h2>
        <div class="mom-grid">
            <div class="mom-card">
                <div class="mom-label">Visualizaciones</div>
                <div class="mom-value">{{ data[-1].visualizaciones_fmt }}</div>
                <div class="mom-diff {{ diff_visualizaciones_clase }}">
                    <i class="fas {{ diff_visualizaciones_icono }}"></i> {{ diff_visualizaciones }}%
                </div>
            </div>
            <div class="mom-card">
                <div class="mom-label">Espectadores</div>
                <div class="mom-value">{{ data[-1].espectadores_fmt }}</div>
                <div class="mom-diff {{ diff_espectadores_clase }}">
                    <i class="fas {{ diff_espectadores_icono }}"></i> {{ diff_espectadores }}%
                </div>
            </div>
            <div class="mom-card">
                <div class="mom-label">Interacciones</div>
                <div class="mom-value">{{ data[-1].interacciones_fmt }}</div>
                <div class="mom-diff {{ diff_interacciones_clase }}">
                    <i class="fas {{ diff_interacciones_icono }}"></i> {{ diff_interacciones }}%
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-info-circle fa-yellow"></i> Datos Insuficientes</h2>
        <p>Solo se encontró registro para 1 mes. Se necesitan al menos 2 meses para mostrar un comparativo.</p>
    </div>
    {% endif %}

    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-chart-bar fa-yellow"></i> Comparativa por Periodo</h2>
        <div class="chart-container">
            <canvas id="tendenciaChart"></canvas>
        </div>
    </div>

    <div class="section-box">
        <h2 class="section-title"><i class="fas fa-table fa-yellow"></i> Desglose Histórico</h2>
        <div class="table-container">
            <table class="modern-table">
                <thead>
                    <tr>
                        <th>Periodo</th>
                        <th>Visualizaciones</th>
                        <th>Espectadores</th>
                        <th>Interacciones</th>
                        <th>Crecimiento</th>
                    </tr>
                </thead>
                <tbody>
                    {% for d in data %}
                    <tr>
                        <td style="font-weight: 600;">{{ d.periodo }}</td>
                        <td>{{ d.visualizaciones_fmt }}</td>
                        <td>{{ d.espectadores_fmt }}</td>
                        <td>{{ d.interacciones_fmt }}</td>
                        <td>
                            {% if d.growth_vis != "N/A" %}
                            <div class="growth-badge {% if d.growth_vis > 0 %}badge-positive{% elif d.growth_vis < 0 %}badge-negative{% else %}badge-neutral{% endif %}">
                                <i class="fas {% if d.growth_vis > 0 %}fa-arrow-up{% elif d.growth_vis < 0 %}fa-arrow-down{% else %}fa-minus{% endif %}"></i>
                                {{ d.growth_vis }}%
                            </div>
                            {% else %}
                            <span style="color: var(--text-secondary); opacity: 0.5;">Inauguración</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
    // Inyectar datos de Python a JS
    const labels = {{ labels | safe }};
    const visualizaciones = {{ chart_visualizaciones | safe }};
    const espectadores = {{ chart_espectadores | safe }};
    const interacciones = {{ chart_interacciones | safe }};

    const ctx = document.getElementById('tendenciaChart').getContext('2d');
    
    // Configuración para que se vea bien en fondo oscuro o claro
    Chart.defaults.color = '#a1a1aa';
    Chart.defaults.font.family = 'Inter';

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Visualizaciones',
                    data: visualizaciones,
                    backgroundColor: '#FFD700',
                    borderColor: '#FFD700',
                    borderWidth: 1,
                    borderRadius: 5
                },
                {
                    label: 'Espectadores',
                    data: espectadores,
                    backgroundColor: '#3b82f6',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 5
                },
                {
                    label: 'Interacciones',
                    data: interacciones,
                    backgroundColor: '#10b981',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
</script>
</body>
</html>
"""

def parse_periodo(periodo_str):
    parts = periodo_str.split(' ')
    if len(parts) == 2:
        mes = parts[0].lower()
        anio = int(parts[1])
        mes_val = MESES_MAP.get(mes, 0)
        return (anio, mes_val)
    return (0, 0)

def format_number(num):
    return "{:,}".format(num)

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cliente', type=str, required=True, help='Nombre formal de la carpeta del cliente (ej. Laura Flores)')
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    testigos_dir = os.path.join(base_dir, "Testigos")
    reportes_dir = os.path.abspath(os.path.join(base_dir, "..", "reportes"))
    
    if not os.path.exists(reportes_dir):
        os.makedirs(reportes_dir)

    cliente_target = args.cliente
    data_list = []

    # Recorrer todos los periodos buscando el cliente
    if os.path.exists(testigos_dir):
        for periodo_folder in os.listdir(testigos_dir):
            periodo_path = os.path.join(testigos_dir, periodo_folder)
            if os.path.isdir(periodo_path):
                cliente_path = os.path.join(periodo_path, cliente_target)
                metrics_file = os.path.join(cliente_path, "metrics.json")
                if os.path.exists(metrics_file):
                    try:
                        with open(metrics_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Extraer datos de ordenacion
                            sort_key = parse_periodo(data.get("periodo", ""))
                            data["_sort"] = sort_key
                            data_list.append(data)
                    except Exception as e:
                        print(f"Error leyendo {metrics_file}: {e}")

    if not data_list:
        print(f"No se encontraron datos historicos (metrics.json) para {cliente_target}")
        return

    # Ordenar cronológicamente
    data_list = sorted(data_list, key=lambda x: x["_sort"])

    # Preparar datos para UI y Chart.js
    labels = []
    c_vis = []
    c_esp = []
    c_int = []

    for i, d in enumerate(data_list):
        d["visualizaciones_fmt"] = format_number(d.get("visualizaciones", 0))
        d["espectadores_fmt"] = format_number(d.get("espectadores", 0))
        d["interacciones_fmt"] = format_number(d.get("interacciones", 0))
        
        # Calcular crecimiento para la tabla
        if i > 0:
            growth = calculate_mom(d["visualizaciones"], data_list[i-1]["visualizaciones"])
            d["growth_vis"] = round(growth, 1)
        else:
            d["growth_vis"] = "N/A"
            
        labels.append(d["periodo"])
        c_vis.append(d.get("visualizaciones", 0))
        c_esp.append(d.get("espectadores", 0))
        c_int.append(d.get("interacciones", 0))

    # Crecimiento MoM (Último mes vs. Anterior)
    diff_visualizaciones = 0
    diff_espectadores = 0
    diff_interacciones = 0

    if len(data_list) > 1:
        current = data_list[-1]
        previous = data_list[-2]
        
        diff_visualizaciones = calculate_mom(current["visualizaciones"], previous["visualizaciones"])
        diff_espectadores = calculate_mom(current["espectadores"], previous["espectadores"])
        diff_interacciones = calculate_mom(current["interacciones"], previous["interacciones"])

    d_vis_cls, d_vis_icn = get_diff_ui(diff_visualizaciones)
    d_esp_cls, d_esp_icn = get_diff_ui(diff_espectadores)
    d_int_cls, d_int_icn = get_diff_ui(diff_interacciones)

    template = Template(HTML_COMPARATIVO_TEMPLATE)
    html_out = template.render(
        cliente=cliente_target,
        data=data_list,
        labels=json.dumps(labels),
        chart_visualizaciones=json.dumps(c_vis),
        chart_espectadores=json.dumps(c_esp),
        chart_interacciones=json.dumps(c_int),
        diff_visualizaciones=f"{diff_visualizaciones:.1f}",
        diff_espectadores=f"{diff_espectadores:.1f}",
        diff_interacciones=f"{diff_interacciones:.1f}",
        diff_visualizaciones_clase=d_vis_cls,
        diff_visualizaciones_icono=d_vis_icn,
        diff_espectadores_clase=d_esp_cls,
        diff_espectadores_icono=d_esp_icn,
        diff_interacciones_clase=d_int_cls,
        diff_interacciones_icono=d_int_icn
    )

    report_filename = f"Reporte_Comparativo_{cliente_target.replace(' ', '_')}.html"
    report_path = os.path.join(reportes_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
        
    print(f"✅ Reporte comparativo guardado en: {report_path}")

if __name__ == "__main__":
    main()
