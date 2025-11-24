import os
import tempfile
import cv2
import numpy as np
from paddleocr import PaddleOCR
import datetime
from spellchecker import SpellChecker
import logging
from config import (
    OCR_LANGUAGE, CONFIDENCE_THRESHOLD, MIN_TEXT_LENGTH,
    PREPROCESS_CONFIG, SPELL_CHECK_ENABLED, SPELL_CHECK_LANGUAGE,
    IMAGE_FOLDER, OUTPUT_FOLDER, PROCESSED_FOLDER,
    VALID_EXTENSIONS, LOG_FILE, LOG_LEVEL
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
    ocr_engine = PaddleOCR(lang=OCR_LANGUAGE, use_angle_cls=True, show_log=False)
    logger.info("Motor OCR inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar PaddleOCR: {e}")
    raise

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
            sharpen=PREPROCESS_CONFIG['sharpen']
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

    # Postprocesamiento: corrección ortográfica y reconstrucción de palabras
    if SPELL_CHECK_ENABLED:
        try:
            spell = SpellChecker(language=SPELL_CHECK_LANGUAGE)
            texto_final = []
            palabras_corregidas_count = 0
            
            for linea in texto_extraido:
                palabras = linea.split()
                palabras_corregidas = []
                for palabra in palabras:
                    # Solo corregir si la palabra no está en el diccionario y no es mayúscula (siglas)
                    if palabra.isalpha() and not palabra.isupper():
                        corregida = spell.correction(palabra)
                        if corregida and corregida != palabra:
                            palabras_corregidas_count += 1
                        palabras_corregidas.append(corregida if corregida else palabra)
                    else:
                        palabras_corregidas.append(palabra)
                texto_final.append(' '.join(palabras_corregidas))
            
            logger.info(f"Corrección ortográfica: {palabras_corregidas_count} palabras corregidas")
        except Exception as e:
            logger.warning(f"Error en corrección ortográfica: {e}. Se usará texto sin corregir.")
            texto_final = texto_extraido
    else:
        texto_final = texto_extraido
        logger.info("Corrección ortográfica desactivada")

    # Unir líneas con salto para mejor legibilidad
    resultado = "\n".join(texto_final).strip()
    logger.info(f"Texto final extraído: {len(resultado)} caracteres")
    return resultado

def process_image_folder(subfolder_path, output_name):
    """
    Procesa todas las imágenes de una carpeta y genera un archivo de texto.
    
    Args:
        subfolder_path: Ruta a la carpeta con imágenes
        output_name: Nombre base para el archivo de salida
    """
    texto_final = f"Procesamiento: {datetime.datetime.now()}\nCarpeta: {output_name}\n\n"
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
                texto = extract_text_paddleocr(full_path)
                if texto:
                    texto_final += f"\n\n### {filename} ###\n\n" + texto
                    imagenes_procesadas += 1
                else:
                    logger.warning(f"No se extrajo texto de {filename}")
                    imagenes_fallidas += 1
            except Exception as e:
                logger.error(f"Error procesando {filename}: {e}", exc_info=True)
                imagenes_fallidas += 1

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        output_file = os.path.join(OUTPUT_FOLDER, f"{output_name}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(texto_final)
        
        logger.info(f"Archivo guardado: {output_file}")
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