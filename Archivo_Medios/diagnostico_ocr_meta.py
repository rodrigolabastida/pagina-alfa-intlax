import pytesseract
from PIL import Image
from pytesseract import Output

img_path = 'Testigos/Abril/Calpulalpan/Meta/Captura de pantalla 2026-05-01 a la(s) 12.04.50 p.m..png'
img = Image.open(img_path)
data = pytesseract.image_to_data(img, lang='spa+eng', config='--psm 6', output_type=Output.DICT)

print(f"{'Text':<30} | {'Top':<5} | {'Left':<5} | {'Width':<5} | {'Height':<5}")
print("-" * 60)
for i in range(len(data['text'])):
    txt = data['text'][i].strip()
    if txt:
        print(f"{txt:<30} | {data['top'][i]:<5} | {data['left'][i]:<5} | {data['width'][i]:<5} | {data['height'][i]:<5}")
