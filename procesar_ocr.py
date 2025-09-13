import os
import tempfile
import cv2
import numpy as np
from paddleocr import PaddleOCR
import datetime
from spellchecker import SpellChecker

# Inicializamos el motor OCR de PaddleOCR para español
ocr_engine = PaddleOCR(lang='es')

def preprocess_image(image_path, contrast_clip=2.0, binarize_block=31, binarize_C=10, denoise_h=20, sharpen=True):
    """
    Preprocesa la imagen para mejorar el resultado del OCR.
    Parámetros:
        contrast_clip: float, límite de ecualización adaptativa (CLAHE)
        binarize_block: int, tamaño de bloque para umbral adaptativo
        binarize_C: int, constante para umbral adaptativo
        denoise_h: int, fuerza de denoising
        sharpen: bool, aplicar filtro de nitidez
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {image_path}")

    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Mejorar contraste usando ecualización adaptativa
    clahe = cv2.createCLAHE(clipLimit=contrast_clip, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # 3. Detectar y corregir rotación (deskew) usando momentos de imagen
    coords = np.column_stack(np.where(gray < 255))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # 4. Mejorar nitidez con filtro de realce (opcional)
    if sharpen:
        kernel_sharpen = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel_sharpen)

    # 5. Umbral adaptativo para binarizar
    thresh = cv2.adaptiveThreshold(gray, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, binarize_block, binarize_C)

    # 6. Apertura morfológica para eliminar ruido pequeño
    kernel = np.ones((2,2), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # 7. Eliminación de ruido de fondo
    denoised = cv2.fastNlMeansDenoising(clean, h=denoise_h)

    return denoised

def extract_text_paddleocr(image_path):
    """
    Extrae texto de una imagen aplicando preprocesamiento y usando PaddleOCR.
    Guarda la imagen preprocesada en 'procesadas/'.
    Filtra resultados de OCR con confianza >= 0.6.
    Devuelve el texto extraído.
    """
    try:
        preprocessed_img = preprocess_image(
            image_path,
            contrast_clip=2.0,
            binarize_block=31,
            binarize_C=10,
            denoise_h=20,
            sharpen=True
        )

        # Guardar imagen preprocesada para control
        output_dir = "procesadas"
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(image_path)
        processed_img_path = os.path.join(output_dir, base_name)
        cv2.imwrite(processed_img_path, preprocessed_img)

        # Guardar temporalmente para OCR (PaddleOCR lee archivo)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
            cv2.imwrite(tmpfile.name, preprocessed_img)
            tmp_img_path = tmpfile.name

        # Ejecutar OCR
        result = ocr_engine.ocr(tmp_img_path)
    except Exception as e:
        print(f"Error al ejecutar OCR en {image_path}: {e}")
        return ""

    texto_extraido = []
    try:
        # Manejo de resultado, que puede variar según versión de Paddle OCR
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            # Formato con diccionarios (nueva versión)
            texts = result[0].get("rec_texts", [])
            scores = result[0].get("rec_scores", [])
            for text, score in zip(texts, scores):
                if score >= 0.7 and text.strip():
                    texto_extraido.append(text.strip())
        else:
            # Formato con listas (versiones anteriores o distinto)
            for region in result:
                if not region or not isinstance(region, list):
                    continue
                for line in region:
                    if (
                        isinstance(line, list)
                        and len(line) >= 2
                        and isinstance(line[1], tuple)
                        and len(line[1]) == 2
                    ):
                        text = line[1][0]
                        confidence = line[1][1]
                        if confidence >= 0.7 and text.strip():
                            texto_extraido.append(text.strip())
        # Filtrar líneas que sean solo números o símbolos (probables falsos positivos)
        texto_extraido = [t for t in texto_extraido if len(t) > 2 and not t.isdigit()]
    except Exception as e:
        print(f"Error procesando líneas OCR en {image_path}: {e}")
        return ""

    # Postprocesamiento: corrección ortográfica y reconstrucción de palabras
    spell = SpellChecker(language='es')
    texto_final = []
    for linea in texto_extraido:
        palabras = linea.split()
        palabras_corregidas = []
        for palabra in palabras:
            # Solo corregir si la palabra no está en el diccionario y no es mayúscula (siglas)
            if palabra.isalpha() and not palabra.isupper():
                corregida = spell.correction(palabra)
                palabras_corregidas.append(corregida if corregida else palabra)
            else:
                palabras_corregidas.append(palabra)
        texto_final.append(' '.join(palabras_corregidas))

    # Unir líneas con salto para mejor legibilidad
    return "\n".join(texto_final).strip()

def process_image_folder(subfolder_path, output_name):
    texto_final = f"Procesamiento: {datetime.datetime.now()}\nCarpeta: {output_name}\n\n"
    print(f"Procesando carpeta: {subfolder_path}")
    for filename in sorted(os.listdir(subfolder_path)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            full_path = os.path.join(subfolder_path, filename)
            print(f"Procesando imagen: {full_path}")
            try:
                texto = extract_text_paddleocr(full_path)
                texto_final += f"\n\n### {filename} ###\n\n" + texto
            except Exception as e:
                print(f"Error con {filename}: {e}")

    output_dir = "texto"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{output_name}.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(texto_final)
    print(f"Archivo final guardado en: {output_file}")

def main():
    base_folder = "image"
    # Buscar todas las subcarpetas dentro de 'image'
    subfolders = [d for d in os.listdir(base_folder)
                  if os.path.isdir(os.path.join(base_folder, d))]

    print(f"Subcarpetas encontradas en '{base_folder}': {subfolders}")

    if not subfolders:
        print("No se encontró ninguna carpeta dentro de 'image/'.")
    else:
        # Procesar cada carpeta
        for subfolder in subfolders:
            full_path = os.path.join(base_folder, subfolder)
            print(f"Procesando subcarpeta: {full_path}")
            process_image_folder(full_path, subfolder)

if __name__ == '__main__':
    # Si se quiere probar una imagen específica, descomentar y ajustar la ruta:
    # test_img = r"C:\\Users\\Usuario\\Documents\\Proyectos\\OCR_Transcriptor\\image\\FBI\\dump_1.jpg"
    # print(extract_text_paddleocr(test_img))
    main()