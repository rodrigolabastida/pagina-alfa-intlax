import os
import shutil
import unicodedata
import re
import pytesseract
from PIL import Image

# Configurar ruta exacta de Tesseract para Mac (Homebrew en procesadores M1/M2 o Intel)
if os.path.exists('/opt/homebrew/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
elif os.path.exists('/usr/local/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'


def normalize_text(text):
    """
    Convierte el texto a minúsculas y elimina los acentos/diacríticos.
    """
    if not text:
        return ""
    # Convertir a minúsculas
    text = text.lower()
    # Eliminar acentos: NFD descompone los caracteres (ej. á -> a + ´), 
    # ignorando las marcas diacríticas (Mn)
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    return text

def extract_period(filename):
    """Extrae el mes y el año del nombre del archivo, ej: '... 2026-05-01 ...' -> 'Mayo_2026'."""
    match = re.search(r'(\d{4})-(\d{2})-\d{2}', filename)
    if match:
        anio = match.group(1)
        mes_num = match.group(2)
        meses = {'01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril', 
                 '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto', 
                 '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'}
        return f"{meses.get(mes_num, 'Desconocido')}_{anio}"
    return "Periodo_Desconocido"

def setup_directories(base_dir):
    """
    Verifica y crea las carpetas de origen y base de destino si no existen.
    """
    source_dir = os.path.join(base_dir, "Testigos_Sin_Procesar")
    dest_dir = os.path.join(base_dir, "Testigos")
    
    # Crear carpeta origen si no existe
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"[!] Carpeta creada: {source_dir}")
        print("[!] Por favor, coloca tus imágenes en esta carpeta y vuelve a ejecutar el script.")
        
    # Crear carpeta principal de destino
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
            
    return source_dir, dest_dir

def classify_image(text):
    """
    Clasifica el texto extraído en una de las categorías definidas en base a palabras clave.
    """
    normalized_text = normalize_text(text)
    
    # Palabras clave normalizadas (sin acentos y en minúsculas)
    if "ana lilia rivera" in normalized_text:
        return "Ana Lilia Rivera"
    elif "calpulalpan" in normalized_text:
        return "Calpulalpan"
    elif "laura flores" in normalized_text:
        return "Laura Flores"
    else:
        return "Otras"

def main():
    # Establecer el directorio base donde se encuentra este mismo script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir, dest_dir = setup_directories(base_dir)
    
    # Extensiones de imagen soportadas
    valid_extensions = ('.jpg', '.jpeg', '.png')
    
    files_to_process = []
    
    # Recoger archivos de Testigos_Sin_Procesar
    if os.path.exists(source_dir):
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(valid_extensions) and not filename.startswith('.'):
                files_to_process.append((os.path.join(source_dir, filename), filename, False))
                
    # Recoger archivos de Testigos de Tiktok
    tiktok_dir = os.path.join(source_dir, "Testigos de Tiktok")
    if os.path.exists(tiktok_dir):
        for filename in os.listdir(tiktok_dir):
            if filename.lower().endswith(valid_extensions) and not filename.startswith('.'):
                files_to_process.append((os.path.join(tiktok_dir, filename), filename, True))
                
    if not files_to_process:
        print(f"\n[!] No se encontraron imágenes listas para procesar en: {source_dir}")
        print("Añade algunas imágenes (jpg, jpeg, png) y reinicia el script.")
        return

    print("\n--- Iniciando el procesamiento y clasificación de imágenes ---")
    
    for file_path, original_filename, is_tiktok in files_to_process:
        print(f"\nProcesando: {original_filename} {'(TikTok)' if is_tiktok else ''}")
        
        try:
            # Abrir imagen
            img = Image.open(file_path)
            
            # Extraer texto usando pytesseract
            text = pytesseract.image_to_string(img, lang='spa+eng')
            
            # Clasificar el texto
            category = classify_image(text)
            
            # Extraer periodo
            periodo = extract_period(original_filename)
            
            print(f"-> Clasificado como: {category} (Periodo: {periodo})")
            
            # Crear carpeta de destino dinámica (Testigos/Periodo/Categoria/Plataforma)
            plataforma = "TikTok" if is_tiktok else "Meta"
            cat_dir = os.path.join(dest_dir, periodo, category, plataforma)
            
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)
            
            final_filename = original_filename
            
            # Mover el archivo a su carpeta correspondiente
            dest_path = os.path.join(cat_dir, final_filename)
            
            # En caso de que el archivo ya exista, evitamos sobreescribir
            counter = 1
            base_name, ext = os.path.splitext(final_filename)
            while os.path.exists(dest_path):
                dest_path = os.path.join(cat_dir, f"{base_name}_{counter}{ext}")
                counter += 1
                
            shutil.move(file_path, dest_path)
            print(f"-> Movido a: {dest_path}")
            
        except pytesseract.pytesseract.TesseractNotFoundError:
            print("Error: No se encuentra Tesseract OCR en el sistema.")
            print("Asegúrate de haberlo instalado (ver instrucciones).")
            break
        except Exception as e:
            print(f"-> [Error] procesando {original_filename}: {str(e)}")

if __name__ == "__main__":
    main()
