import os
import cv2
import easyocr
from spellchecker import SpellChecker

# Rutas
BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_IMAGENES = os.path.join(BASE, 'image')
CARPETA_TEXTO = os.path.join(BASE, 'texto')
ARCHIVO_SALIDA = os.path.join(CARPETA_TEXTO, 'todo_el_texto.txt')

# Crear carpeta de salida si no existe
os.makedirs(CARPETA_TEXTO, exist_ok=True)

# Inicializar OCR y corrector ortográfico
reader = easyocr.Reader(['es'])
spell = SpellChecker(language='es')

# Extensiones de imagen válidas
EXT_VALIDAS = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']

# Función de preprocesamiento con OpenCV
def preprocesar_imagen(ruta):
    img = cv2.imread(ruta)
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ruta_temp = os.path.join(BASE, 'temp.jpg')
    cv2.imwrite(ruta_temp, binaria)
    return ruta_temp

# Corrección ortográfica
def corregir_texto(texto):
    palabras = texto.split()
    corregidas = []
    for palabra in palabras:
        if palabra.isalpha():
            corregidas.append(spell.correction(palabra) or palabra)
        else:
            corregidas.append(palabra)
    return ' '.join(corregidas)

# Procesamiento principal
texto_final = ''
for archivo in sorted(os.listdir(CARPETA_IMAGENES)):
    nombre, ext = os.path.splitext(archivo)
    if ext.lower() in EXT_VALIDAS:
        print(f'Procesando {archivo}...')
        ruta_original = os.path.join(CARPETA_IMAGENES, archivo)
        ruta_proc = preprocesar_imagen(ruta_original)

        texto_detectado = reader.readtext(ruta_proc, detail=0)
        texto_unido = '\n'.join(texto_detectado)
        texto_corregido = corregir_texto(texto_unido)

        texto_final += f'\n--- {archivo} ---\n'
        texto_final += texto_corregido + '\n'

# Guardar resultado final
with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
    f.write(texto_final.strip())

print('\n Todo el texto fue guardado en:', ARCHIVO_SALIDA)