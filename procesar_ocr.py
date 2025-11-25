import os
import tempfile
import cv2
import numpy as np
from paddleocr import PaddleOCR
import datetime
from spellchecker import SpellChecker
import logging
import re
from config import (
    OCR_LANGUAGE, CONFIDENCE_THRESHOLD, MIN_TEXT_LENGTH,
    PREPROCESS_CONFIG, SPELL_CHECK_ENABLED, SPELL_CHECK_LANGUAGE,
    IMAGE_FOLDER, OUTPUT_FOLDER, PROCESSED_FOLDER,
    VALID_EXTENSIONS, LOG_FILE, LOG_LEVEL,
    GENERATE_RAW_OUTPUT, AGGRESSIVE_CLEANING
)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializamos el motor OCR de PaddleOCR
try:
    ocr_engine = PaddleOCR(lang=OCR_LANGUAGE, use_textline_orientation=True)
    logger.info("Motor OCR inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar PaddleOCR: {e}")
    raise

def preprocess_image(image_path, contrast_clip=2.0, binarize_block=31, binarize_C=10, denoise_h=20, sharpen=True, deskew=True, dilate_erode=False):
    """
    Preprocesa la imagen para mejorar el resultado del OCR.
    Parámetros:
        contrast_clip: float, límite de ecualización adaptativa (CLAHE). 1.0 = sin cambio
        binarize_block: int, tamaño de bloque para umbral adaptativo. 0 = desactivado
        binarize_C: int, constante para umbral adaptativo
        denoise_h: int, fuerza de denoising. 0 = desactivado
        sharpen: bool, aplicar filtro de nitidez
        deskew: bool, aplicar corrección de rotación automática
        dilate_erode: bool, aplicar operaciones morfológicas para conectar letras fragmentadas
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {image_path}")

    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Mejorar contraste usando ecualización adaptativa (solo si contrast_clip > 1.0)
    if contrast_clip > 1.0:
        clahe = cv2.createCLAHE(clipLimit=contrast_clip, tileGridSize=(8,8))
        gray = clahe.apply(gray)

    # 3. Detectar y corregir rotación (deskew) usando momentos de imagen (solo si está activado)
    if deskew:
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

    # 5. Umbral adaptativo para binarizar (solo si binarize_block > 0)
    if binarize_block > 0:
        thresh = cv2.adaptiveThreshold(gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, binarize_block, binarize_C)
    else:
        thresh = gray  # Mantener escala de grises sin binarizar

    # 6. Apertura morfológica para eliminar ruido pequeño (solo si se binarizó)
    if binarize_block > 0:
        kernel = np.ones((2,2), np.uint8)
        clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    else:
        clean = thresh

    # 6b. Dilate/Erode para conectar letras fragmentadas (solo para documentos históricos)
    if dilate_erode and binarize_block > 0:
        # Dilatar para conectar componentes cercanos
        kernel_dilate = np.ones((2,2), np.uint8)
        clean = cv2.dilate(clean, kernel_dilate, iterations=1)
        # Erosionar para volver al tamaño original
        kernel_erode = np.ones((2,2), np.uint8)
        clean = cv2.erode(clean, kernel_erode, iterations=1)

    # 7. Eliminación de ruido de fondo (solo si denoise_h > 0)
    if denoise_h > 0:
        denoised = cv2.fastNlMeansDenoising(clean, h=denoise_h)
    else:
        denoised = clean

    return denoised

def clean_ocr_artifacts(text, aggressive=False):
    """
    Limpia artefactos comunes del OCR.
    
    Args:
        text: Texto a limpiar
        aggressive: Si True, aplica limpieza más agresiva para documentos deteriorados
    
    Returns:
        str: Texto limpiado
    """
    if not text:
        return text
    
    # Correcciones básicas comunes
    replacements = {
        'n0': 'no',
        'N0': 'NO', 
        'o0': 'oo',
        'O0': 'OO',
        '0o': 'oo',
        '0O': 'OO',
        'l0': 'lo',
        'L0': 'LO',
        '0l': 'ol',
        '0L': 'OL',
        'rn': 'm',  # común en OCR
        '|': 'I',   # barras verticales confundidas con I
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    if aggressive:
        # Remover caracteres sueltos (probable ruido)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Eliminar líneas con solo 1-2 caracteres que sean símbolos o números sueltos
            if len(line.strip()) <= 2 and not line.strip().isalpha():
                continue
            # Eliminar símbolos aleatorios comunes del OCR
            line = re.sub(r'[~`´¨^°]', '', line)
            # Eliminar espacios múltiples
            line = re.sub(r'\s{2,}', ' ', line)
            cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
    
    return text

def reconstruct_broken_words(lines):
    """
    Intenta reconstruir palabras partidas entre líneas.
    
    Args:
        lines: Lista de líneas de texto
    
    Returns:
        list: Líneas con palabras reconstruidas
    """
    if len(lines) < 2:
        return lines
    
    reconstructed = []
    i = 0
    while i < len(lines):
        current_line = lines[i].strip()
        
        # Si la línea actual termina con guión, intentar unir con la siguiente
        if i < len(lines) - 1 and current_line.endswith('-'):
            next_line = lines[i + 1].strip()
            # Unir removiendo el guión
            combined = current_line[:-1] + next_line
            reconstructed.append(combined)
            i += 2
        # Si la línea termina con una palabra incompleta (sin puntuación)
        elif i < len(lines) - 1 and current_line and not current_line[-1] in '.,:;!?':
            next_line = lines[i + 1].strip()
            # Si la siguiente línea empieza con minúscula, probablemente es continuación
            if next_line and next_line[0].islower():
                combined = current_line + next_line
                reconstructed.append(combined)
                i += 2
            else:
                reconstructed.append(current_line)
                i += 1
        else:
            reconstructed.append(current_line)
            i += 1
    
    return reconstructed

def extract_text_paddleocr(image_path, confidence_threshold=CONFIDENCE_THRESHOLD):
    """
    Extrae texto de una imagen aplicando preprocesamiento y usando PaddleOCR.
    Guarda la imagen preprocesada en 'procesadas/'.
    Filtra resultados de OCR con confianza >= confidence_threshold.
    
    Args:
        image_path: Ruta a la imagen a procesar
        confidence_threshold: Umbral de confianza para filtrar resultados (default: 0.7)
    
    Returns:
        str: Texto extraído y procesado
    """
    try:
        logger.info(f"Procesando imagen: {os.path.basename(image_path)}")
        preprocessed_img = preprocess_image(
            image_path,
            contrast_clip=PREPROCESS_CONFIG['contrast_clip'],
            binarize_block=PREPROCESS_CONFIG['binarize_block'],
            binarize_C=PREPROCESS_CONFIG['binarize_C'],
            denoise_h=PREPROCESS_CONFIG['denoise_h'],
            sharpen=PREPROCESS_CONFIG['sharpen'],
            deskew=PREPROCESS_CONFIG['deskew'],
            dilate_erode=PREPROCESS_CONFIG.get('dilate_erode', False)
        )

        # Guardar imagen preprocesada para control
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)
        base_name = os.path.basename(image_path)
        processed_img_path = os.path.join(PROCESSED_FOLDER, base_name)
        cv2.imwrite(processed_img_path, preprocessed_img)
        logger.debug(f"Imagen preprocesada guardada en: {processed_img_path}")

        # Guardar temporalmente para OCR (PaddleOCR lee archivo)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
            cv2.imwrite(tmpfile.name, preprocessed_img)
            tmp_img_path = tmpfile.name

        # Ejecutar OCR
        result = ocr_engine.ocr(tmp_img_path)
        
        # Limpiar archivo temporal
        try:
            os.unlink(tmp_img_path)
        except Exception:
            pass
            
    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {image_path}")
        return ""
    except cv2.error as e:
        logger.error(f"Error de OpenCV en {image_path}: {e}")
        return ""
    except Exception as e:
        logger.error(f"Error al ejecutar OCR en {image_path}: {e}")
        return ""

    texto_extraido = []
    try:
        # Manejo de resultado, que puede variar según versión de Paddle OCR
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            # Formato con diccionarios (nueva versión)
            texts = result[0].get("rec_texts", [])
            scores = result[0].get("rec_scores", [])
            for text, score in zip(texts, scores):
                if score >= confidence_threshold and text.strip():
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
                        if confidence >= confidence_threshold and text.strip():
                            texto_extraido.append(text.strip())
        # Filtrar líneas que sean solo números o símbolos (probables falsos positivos)
        texto_extraido = [t for t in texto_extraido if len(t) > MIN_TEXT_LENGTH and not t.isdigit()]
        logger.info(f"Extraídas {len(texto_extraido)} líneas de texto con confianza >= {confidence_threshold}")
    except Exception as e:
        logger.error(f"Error procesando líneas OCR en {image_path}: {e}")
        return ""

    # VERSIÓN RAW: texto crudo sin postprocesamiento (solo limpieza básica)
    texto_raw = '\n'.join(texto_extraido)
    
    # Postprocesamiento: corrección ortográfica y reconstrucción de palabras
    if SPELL_CHECK_ENABLED:
        try:
            spell = SpellChecker(language=SPELL_CHECK_LANGUAGE)
            texto_final = []
            palabras_corregidas_count = 0
            
            # Primero limpiar artefactos del OCR
            texto_extraido_limpio = []
            for linea in texto_extraido:
                linea_limpia = clean_ocr_artifacts(linea, aggressive=AGGRESSIVE_CLEANING)
                if linea_limpia.strip():
                    texto_extraido_limpio.append(linea_limpia)
            
            # Intentar reconstruir palabras partidas
            texto_extraido_reconstruido = reconstruct_broken_words(texto_extraido_limpio)
            
            for linea in texto_extraido_reconstruido:
                palabras = linea.split()
                palabras_corregidas = []
                for palabra in palabras:
                    # Limpiar puntuación para corrección
                    palabra_limpia = palabra.strip('.,;:!?()[]{}«»""\'')
                    # Solo corregir si la palabra no está en el diccionario y no es mayúscula (siglas)
                    if palabra_limpia and palabra_limpia.isalpha() and not palabra_limpia.isupper() and len(palabra_limpia) > 2:
                        corregida = spell.correction(palabra_limpia)
                        if corregida and corregida != palabra_limpia:
                            # Preservar puntuación original
                            palabra = palabra.replace(palabra_limpia, corregida)
                            palabras_corregidas_count += 1
                    palabras_corregidas.append(palabra)
                texto_final.append(' '.join(palabras_corregidas))
            
            logger.info(f"Corrección ortográfica: {palabras_corregidas_count} palabras corregidas")
        except Exception as e:
            logger.warning(f"Error en corrección ortográfica: {e}. Se usará texto sin corregir.")
            texto_final = texto_extraido
    else:
        # Sin corrección ortográfica, pero aplicar limpieza si está activada
        if AGGRESSIVE_CLEANING:
            texto_extraido_limpio = [clean_ocr_artifacts(linea, aggressive=True) for linea in texto_extraido]
            texto_final = reconstruct_broken_words(texto_extraido_limpio)
        else:
            texto_final = texto_extraido
        logger.info("Corrección ortográfica desactivada")

    # Unir líneas con salto para mejor legibilidad
    resultado_procesado = "\n".join(texto_final).strip()
    logger.info(f"Texto final extraído: {len(resultado_procesado)} caracteres")
    
    # Retornar tupla con versión raw y procesada
    return (texto_raw, resultado_procesado)

def process_image_folder(subfolder_path, output_name):
    """
    Procesa todas las imágenes de una carpeta y genera un archivo de texto.
    
    Args:
        subfolder_path: Ruta a la carpeta con imágenes
        output_name: Nombre base para el archivo de salida
    """
    texto_procesado = f"Procesamiento: {datetime.datetime.now()}\nCarpeta: {output_name}\n\n"
    texto_raw = f"Procesamiento: {datetime.datetime.now()}\nCarpeta: {output_name}\nVERSIÓN RAW (sin postprocesar)\n\n"
    logger.info(f"=== Procesando carpeta: {subfolder_path} ===")
    
    imagenes_procesadas = 0
    imagenes_fallidas = 0
    
    try:
        archivos = sorted(os.listdir(subfolder_path))
        imagenes = [f for f in archivos if f.lower().endswith(VALID_EXTENSIONS)]
        
        if not imagenes:
            logger.warning(f"No se encontraron imágenes válidas en {subfolder_path}")
            return
        
        logger.info(f"Encontradas {len(imagenes)} imágenes para procesar")
        
        for filename in imagenes:
            full_path = os.path.join(subfolder_path, filename)
            try:
                resultado = extract_text_paddleocr(full_path)
                # Ahora extract_text_paddleocr retorna tupla (raw, procesado)
                if isinstance(resultado, tuple):
                    raw_text, processed_text = resultado
                    if processed_text:
                        texto_procesado += f"\n\n### {filename} ###\n\n" + processed_text
                        if GENERATE_RAW_OUTPUT:
                            texto_raw += f"\n\n### {filename} ###\n\n" + raw_text
                        imagenes_procesadas += 1
                    else:
                        logger.warning(f"No se extrajo texto de {filename}")
                        imagenes_fallidas += 1
                else:
                    # Compatibilidad con versión anterior (por si acaso)
                    if resultado:
                        texto_procesado += f"\n\n### {filename} ###\n\n" + resultado
                        imagenes_procesadas += 1
                    else:
                        imagenes_fallidas += 1
            except Exception as e:
                logger.error(f"Error procesando {filename}: {e}", exc_info=True)
                imagenes_fallidas += 1

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Guardar versión procesada
        output_file = os.path.join(OUTPUT_FOLDER, f"{output_name}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(texto_procesado)
        logger.info(f"Archivo procesado guardado: {output_file}")
        
        # Guardar versión raw si está activada
        if GENERATE_RAW_OUTPUT:
            output_file_raw = os.path.join(OUTPUT_FOLDER, f"{output_name}_RAW.txt")
            with open(output_file_raw, "w", encoding="utf-8") as f:
                f.write(texto_raw)
            logger.info(f"Archivo RAW guardado: {output_file_raw}")
        
        logger.info(f"Resumen - Procesadas: {imagenes_procesadas}, Fallidas: {imagenes_fallidas}")
        
    except Exception as e:
        logger.error(f"Error procesando carpeta {subfolder_path}: {e}", exc_info=True)

def main():
    """
    Función principal que procesa todas las subcarpetas en 'image/'.
    """
    logger.info("="*50)
    logger.info("Iniciando proceso de OCR")
    logger.info("="*50)
    
    if not os.path.exists(IMAGE_FOLDER):
        logger.error(f"La carpeta '{IMAGE_FOLDER}' no existe. Creándola...")
        os.makedirs(IMAGE_FOLDER, exist_ok=True)
        logger.info(f"Carpeta '{IMAGE_FOLDER}' creada. Por favor, agregá las imágenes a procesar.")
        return
    
    # Buscar todas las subcarpetas dentro de 'image'
    try:
        subfolders = [d for d in os.listdir(IMAGE_FOLDER)
                      if os.path.isdir(os.path.join(IMAGE_FOLDER, d))]
    except Exception as e:
        logger.error(f"Error al leer la carpeta '{IMAGE_FOLDER}': {e}")
        return

    logger.info(f"Subcarpetas encontradas en '{IMAGE_FOLDER}': {subfolders}")

    if not subfolders:
        logger.warning(f"No se encontró ninguna carpeta dentro de '{IMAGE_FOLDER}/'.")
        logger.info("Creá una subcarpeta dentro de 'image/' y agregá las imágenes a procesar.")
    else:
        # Procesar cada carpeta
        carpetas_procesadas = 0
        for subfolder in subfolders:
            full_path = os.path.join(IMAGE_FOLDER, subfolder)
            try:
                process_image_folder(full_path, subfolder)
                carpetas_procesadas += 1
            except Exception as e:
                logger.error(f"Error al procesar subcarpeta {subfolder}: {e}", exc_info=True)
        
        logger.info("="*50)
        logger.info(f"Proceso finalizado. Carpetas procesadas: {carpetas_procesadas}/{len(subfolders)}")
        logger.info("="*50)

if __name__ == '__main__':
    # Si se quiere probar una imagen específica, descomentar y ajustar la ruta:
    # test_img = r"C:\\Users\\Usuario\\Documents\\Proyectos\\OCR_Transcriptor\\image\\FBI\\dump_1.jpg"
    # print(extract_text_paddleocr(test_img))
    main()