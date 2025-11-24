"""
Configuración centralizada para el procesador OCR.
Modificá estos valores según tus necesidades.
"""

# Configuración de OCR
OCR_LANGUAGE = 'es'  # Idioma para PaddleOCR
CONFIDENCE_THRESHOLD = 0.7  # Umbral de confianza (0.0 - 1.0)
MIN_TEXT_LENGTH = 2  # Longitud mínima de texto aceptado

# Configuración de preprocesamiento
PREPROCESS_CONFIG = {
    'contrast_clip': 2.0,      # Límite de ecualización adaptativa (CLAHE)
    'binarize_block': 31,      # Tamaño de bloque para umbral adaptativo (debe ser impar)
    'binarize_C': 10,          # Constante para umbral adaptativo
    'denoise_h': 20,           # Fuerza de denoising (mayor = más suavizado)
    'sharpen': True            # Aplicar filtro de nitidez
}

# Configuración de corrección ortográfica
SPELL_CHECK_ENABLED = True     # Activar/desactivar corrección ortográfica
SPELL_CHECK_LANGUAGE = 'es'    # Idioma para corrección ortográfica

# Configuración de carpetas
IMAGE_FOLDER = 'image'          # Carpeta de entrada con imágenes
OUTPUT_FOLDER = 'texto'         # Carpeta de salida con textos
PROCESSED_FOLDER = 'procesadas' # Carpeta con imágenes preprocesadas

# Extensiones de imagen válidas
VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')

# Configuración de logging
LOG_FILE = 'ocr_process.log'
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
