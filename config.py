"""
Configuración centralizada para el procesador OCR.
Modificá estos valores según tus necesidades.
"""

# ==============================================================================
# PERFIL DE CONFIGURACIÓN
# ==============================================================================
# Descomentá el perfil que necesites usar:

# PERFIL 1: Documentos de ALTA CALIDAD (PDFs escaneados nítidos, modernos)
# PERFIL_ACTIVO = "ALTA_CALIDAD"

# PERFIL 2: Documentos HISTÓRICOS (papel viejo, manchas, bajo contraste, ruido)
PERFIL_ACTIVO = "HISTORICOS"

# ==============================================================================
# PERFILES PREDEFINIDOS
# ==============================================================================

PERFILES = {
    "ALTA_CALIDAD": {
        "ocr_language": "en",
        "confidence_threshold": 0.75,
        "min_text_length": 2,
        "preprocess": {
            'contrast_clip': 1.0,      # Sin mejora de contraste
            'binarize_block': 0,       # Sin binarización
            'binarize_C': 2,
            'denoise_h': 0,            # Sin reducción de ruido
            'sharpen': False,          # Sin nitidez
            'deskew': False,           # Sin corrección de rotación
            'dilate_erode': False      # Sin operaciones morfológicas
        },
        "spell_check_enabled": False,
        "spell_check_language": "en",
        "generate_raw_output": False,
        "aggressive_cleaning": False
    },
    
    "HISTORICOS": {
        "ocr_language": "es",
        "confidence_threshold": 0.50,   # Muy permisivo para capturar todo el texto posible
        "min_text_length": 1,           # Capturar incluso letras sueltas
        "preprocess": {
            'contrast_clip': 3.0,       # Contraste moderado
            'binarize_block': 25,       # Binarización menos agresiva (debe ser impar)
            'binarize_C': 8,            # Ajuste suave
            'denoise_h': 20,            # Reducción de ruido moderada
            'sharpen': True,            # Nitidez para texto borroso
            'deskew': True,             # Corrección de rotación
            'dilate_erode': False       # DESACTIVADO - causa pérdida de texto
        },
        "spell_check_enabled": False,   # DESACTIVADO - causa más errores que aciertos
        "spell_check_language": "es",
        "generate_raw_output": True,    # Genera versión sin postprocesar (IMPORTANTE)
        "aggressive_cleaning": False    # DESACTIVADO - elimina texto válido
    }
}

# Cargar configuración del perfil activo
PERFIL = PERFILES[PERFIL_ACTIVO]

# Configuración de OCR
OCR_LANGUAGE = PERFIL["ocr_language"]
CONFIDENCE_THRESHOLD = PERFIL["confidence_threshold"]
MIN_TEXT_LENGTH = PERFIL["min_text_length"]

# Configuración de preprocesamiento
PREPROCESS_CONFIG = PERFIL["preprocess"]

# Configuración de corrección ortográfica
SPELL_CHECK_ENABLED = PERFIL["spell_check_enabled"]
SPELL_CHECK_LANGUAGE = PERFIL["spell_check_language"]

# Configuración de salida
GENERATE_RAW_OUTPUT = PERFIL.get("generate_raw_output", False)
AGGRESSIVE_CLEANING = PERFIL.get("aggressive_cleaning", False)

# Configuración de carpetas
IMAGE_FOLDER = 'image'          # Carpeta de entrada con imágenes
OUTPUT_FOLDER = 'texto'         # Carpeta de salida con textos
PROCESSED_FOLDER = 'procesadas' # Carpeta con imágenes preprocesadas

# Extensiones de imagen válidas
VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')

# Configuración de logging
LOG_FILE = 'ocr_process.log'
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ==============================================================================
# GUÍA DE USO
# ==============================================================================
"""
CÓMO CAMBIAR DE PERFIL:
1. Editá la línea "PERFIL_ACTIVO" al inicio del archivo
2. Descomentá el perfil que necesites (borrá el #)
3. Comentá el otro perfil (agregá # al inicio)

PARA DOCUMENTOS HISTÓRICOS (dictadura uruguaya):
    PERFIL_ACTIVO = "HISTORICOS"
    - Preprocesamiento agresivo para papel viejo
    - Corrección ortográfica activada (español)
    - Umbral de confianza bajo (captura más texto aunque tenga errores)

PARA DOCUMENTOS MODERNOS (PDFs nítidos):
    PERFIL_ACTIVO = "ALTA_CALIDAD"
    - Preprocesamiento mínimo (mantiene calidad original)
    - Sin corrección ortográfica
    - Umbral de confianza alto (solo texto muy preciso)

AJUSTES FINOS (si los resultados no son óptimos):
- Si captura POCO TEXTO: bajar confidence_threshold (ej: 0.50)
- Si hay MUCHO RUIDO: subir denoise_h (ej: 40)
- Si texto está BORROSO: activar sharpen = True
- Si imágenes están TORCIDAS: activar deskew = True
- Si hay MANCHAS/MARCAS: subir binarize_block (ej: 41, 51)

CREAR TU PROPIO PERFIL:
Podés agregar un nuevo perfil en el diccionario PERFILES copiando la estructura
de los existentes y ajustando los valores según tus necesidades.
"""
