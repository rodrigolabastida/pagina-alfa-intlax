import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generador_reportes import process_folder_and_generate_report

base_dir = os.path.dirname(os.path.abspath(__file__))
testigos_dir = os.path.join(base_dir, "Testigos")

for periodo_folder in os.listdir(testigos_dir):
    periodo_path = os.path.join(testigos_dir, periodo_folder)
    if os.path.isdir(periodo_path):
        periodo_formal = periodo_folder.replace("_", " ")
        for cliente_folder in os.listdir(periodo_path):
            cliente_path = os.path.join(periodo_path, cliente_folder)
            if os.path.isdir(cliente_path):
                # Ignorar carpetas vacias o sin imagenes png/jpg
                if any(f.endswith('.png') or f.endswith('.jpg') for f in os.listdir(cliente_path)):
                    print(f"Procesando historico: {periodo_formal} - {cliente_folder}")
                    # Lugar genérico
                    lugar = "Tlaxcala"
                    if cliente_folder == "Calpulalpan":
                        lugar = "Calpulalpan, Tlaxcala"
                    process_folder_and_generate_report(cliente_path, cliente_folder, base_dir, cliente_folder, periodo_formal, lugar)
