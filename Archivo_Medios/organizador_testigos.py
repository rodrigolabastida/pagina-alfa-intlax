import os
import shutil
import unicodedata
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

def setup_directories(base_dir):
    """
    Verifica y crea las carpetas de origen y destino si no existen.
    """
    source_dir = os.path.join(base_dir, "Testigos_Sin_Procesar")
    dest_dir = os.path.join(base_dir, "Testigos")
    
    categories = [
        "Ana Lilia Rivera",
        "Calpulalpan",
        "Benito Juarez o Ruben Becerra",
        "Otras"
    ]
    
    # Crear carpeta origen si no existe
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"[!] Carpeta creada: {source_dir}")
        print("[!] Por favor, coloca tus imágenes en esta carpeta y vuelve a ejecutar el script.")
        
    # Crear carpeta principal de destino y subcarpetas
    for category in categories:
        cat_dir = os.path.join(dest_dir, category)
        if not os.path.exists(cat_dir):
            os.makedirs(cat_dir)
            print(f"[✓] Carpeta destino creada: {cat_dir}")
            
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
    elif "benito juarez" in normalized_text or "ruben becerra" in normalized_text:
        return "Benito Juarez o Ruben Becerra"
    else:
        return "Otras"

def main():
    # Establecer el directorio base donde se encuentra este mismo script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir, dest_dir = setup_directories(base_dir)
    
    # Extensiones de imagen soportadas
    valid_extensions = ('.jpg', '.jpeg', '.png')
    
    if not os.path.exists(source_dir) or not os.listdir(source_dir):
        print(f"\n[!] No se encontraron imágenes listas para procesar en: {source_dir}")
        print("Añade algunas imágenes (jpg, jpeg, png) y reinicia el script.")
        return

    print("\n--- Iniciando el procesamiento y clasificación de imágenes ---")
    
    for filename in os.listdir(source_dir):
        # Ignorar archivos ocultos o que no sean imágenes soportadas
        if filename.lower().endswith(valid_extensions) and not filename.startswith('.'):
            file_path = os.path.join(source_dir, filename)
            print(f"\nProcesando: {filename}")
            
            try:
                # Abrir imagen
                img = Image.open(file_path)
                
                # Extraer texto usando pytesseract (con idioma español si está disponible)
                # Si no está instalado el paquete de español, puedes usar solo lang='eng' (por defecto)
                text = pytesseract.image_to_string(img, lang='spa+eng')
                
                # Clasificar el texto
                category = classify_image(text)
                print(f"-> Clasificado como: {category}")
                
                # Mover el archivo a su carpeta correspondiente
                dest_path = os.path.join(dest_dir, category, filename)
                
                # En caso de que el archivo ya exista en el destino, evitamos sobreescribir generando un nuevo nombre
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(dest_path):
                    dest_path = os.path.join(dest_dir, category, f"{base_name}_{counter}{ext}")
                    counter += 1
                    
                shutil.move(file_path, dest_path)
                print(f"-> Movido a: {dest_path}")
                
            except pytesseract.pytesseract.TesseractNotFoundError:
                print("Error: No se encuentra Tesseract OCR en el sistema.")
                print("Asegúrate de haberlo instalado (ver instrucciones).")
                break
            except Exception as e:
                print(f"-> [Error] procesando {filename}: {str(e)}")

if __name__ == "__main__":
    main()
