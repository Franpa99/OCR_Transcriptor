"""
API Flask para el procesamiento OCR
Expone endpoints para que la interfaz web pueda procesar imágenes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

# Importar funciones del script original
from procesar_ocr import (
    preprocess_image, 
    perform_ocr, 
    clean_ocr_artifacts,
    reconstruct_broken_words,
    spell_check_text,
    ocr_engine
)
from config import PREPROCESS_CONFIG, CONFIDENCE_THRESHOLD, MIN_TEXT_LENGTH, PERFILES

# Configurar Flask
app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión válida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    """Página de inicio con información de la API"""
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OCR Transcriptor API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #4f46e5; }
            .endpoint {
                background: #f9fafb;
                padding: 15px;
                border-left: 4px solid #4f46e5;
                margin: 15px 0;
                border-radius: 5px;
            }
            code {
                background: #e5e7eb;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            .status-ok {
                color: #10b981;
                font-weight: bold;
            }
            a {
                color: #4f46e5;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 OCR Transcriptor API</h1>
            <p>Backend activo y funcionando. <span class="status-ok">✓ Online</span></p>
            
            <h2>Endpoints disponibles:</h2>
            
            <div class="endpoint">
                <strong>GET /health</strong>
                <p>Verificar estado del servidor</p>
            </div>
            
            <div class="endpoint">
                <strong>POST /process</strong>
                <p>Procesar imágenes con OCR</p>
                <p>Parámetros:</p>
                <ul>
                    <li><code>files</code>: Archivos de imagen</li>
                    <li><code>profile</code>: HISTORICOS o ALTA_CALIDAD</li>
                    <li><code>language</code>: es o en</li>
                </ul>
            </div>
            
            <div class="endpoint">
                <strong>GET /profiles</strong>
                <p>Obtener perfiles de procesamiento disponibles</p>
            </div>
            
            <h2>Frontend</h2>
            <p>Para usar la interfaz web, visita:</p>
            <p><a href="https://franpa99.github.io/OCR_Transcriptor/">https://franpa99.github.io/OCR_Transcriptor/</a></p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
            
            <p style="text-align: center; color: #6b7280;">
                Desarrollado con PaddleOCR | 
                <a href="https://github.com/Franpa99/OCR_Transcriptor" target="_blank">GitHub</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Servidor OCR funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/process', methods=['POST'])
def process_images():
    """
    Endpoint principal para procesar imágenes con OCR
    
    Recibe:
    - files: Lista de archivos de imagen
    - profile: Perfil de procesamiento (HISTORICOS o ALTA_CALIDAD)
    - language: Idioma (es o en)
    
    Retorna:
    - text: Texto extraído
    - filename: Nombre sugerido para el archivo de salida
    """
    try:
        # Verificar que se enviaron archivos
        if 'files' not in request.files:
            return jsonify({'error': 'No se enviaron archivos'}), 400
        
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({'error': 'La lista de archivos está vacía'}), 400
        
        # Obtener configuración
        profile = request.form.get('profile', 'HISTORICOS')
        language = request.form.get('language', 'es')
        
        # Validar perfil
        if profile not in PERFILES:
            return jsonify({'error': f'Perfil inválido: {profile}'}), 400
        
        # Obtener configuración del perfil
        perfil_config = PERFILES[profile]
        preprocess_config = perfil_config['preprocess']
        confidence_threshold = perfil_config['confidence_threshold']
        min_text_length = perfil_config['min_text_length']
        spell_check_enabled = perfil_config['spell_check_enabled']
        spell_check_language = language if spell_check_enabled else None
        aggressive_cleaning = perfil_config['aggressive_cleaning']
        
        logger.info(f"Procesando {len(files)} archivo(s) con perfil {profile} e idioma {language}")
        
        # Crear directorio temporal para procesamiento
        temp_dir = tempfile.mkdtemp()
        processed_dir = os.path.join(temp_dir, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        
        all_text = []
        processed_count = 0
        
        try:
            # Procesar cada archivo
            for file in files:
                if not file or file.filename == '':
                    continue
                
                if not allowed_file(file.filename):
                    logger.warning(f"Archivo ignorado (extensión no válida): {file.filename}")
                    continue
                
                # Guardar archivo temporal
                filename = secure_filename(file.filename)
                temp_path = os.path.join(temp_dir, filename)
                file.save(temp_path)
                
                # Verificar tamaño
                if os.path.getsize(temp_path) > MAX_FILE_SIZE:
                    logger.warning(f"Archivo muy grande: {filename}")
                    continue
                
                logger.info(f"Procesando: {filename}")
                
                # Preprocesar imagen
                try:
                    preprocessed_path = os.path.join(processed_dir, filename)
                    preprocessed_img = preprocess_image(temp_path, **preprocess_config)
                    
                    import cv2
                    cv2.imwrite(preprocessed_path, preprocessed_img)
                    
                    # Realizar OCR
                    results = ocr_engine.ocr(preprocessed_path, cls=True)
                    
                    if results and results[0]:
                        for line in results[0]:
                            if line and len(line) >= 2:
                                text, confidence = line[1]
                                
                                if confidence >= confidence_threshold and len(text) >= min_text_length:
                                    all_text.append(text)
                        
                        processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error procesando {filename}: {e}")
                    continue
            
            if processed_count == 0:
                return jsonify({'error': 'No se pudo procesar ningún archivo'}), 400
            
            # Unir y limpiar texto
            full_text = '\n'.join(all_text)
            
            # Aplicar limpieza de artefactos
            full_text = clean_ocr_artifacts(full_text, aggressive=aggressive_cleaning)
            
            # Reconstruir palabras partidas
            lines = full_text.split('\n')
            lines = reconstruct_broken_words(lines)
            full_text = '\n'.join(lines)
            
            # Aplicar corrección ortográfica si está habilitada
            if spell_check_enabled and spell_check_language:
                try:
                    full_text = spell_check_text(full_text, spell_check_language)
                except Exception as e:
                    logger.warning(f"Error en corrección ortográfica: {e}")
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f'transcripcion_{timestamp}.txt'
            
            logger.info(f"Procesamiento completado exitosamente. {processed_count} archivo(s) procesado(s)")
            
            return jsonify({
                'text': full_text,
                'filename': output_filename,
                'files_processed': processed_count,
                'profile': profile,
                'language': language
            })
        
        finally:
            # Limpiar archivos temporales
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Error limpiando archivos temporales: {e}")
    
    except Exception as e:
        logger.error(f"Error en proceso OCR: {e}", exc_info=True)
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/profiles', methods=['GET'])
def get_profiles():
    """Obtener lista de perfiles disponibles"""
    profiles = {}
    for name, config in PERFILES.items():
        profiles[name] = {
            'name': name,
            'language': config['ocr_language'],
            'confidence_threshold': config['confidence_threshold'],
            'spell_check_enabled': config['spell_check_enabled']
        }
    return jsonify(profiles)

if __name__ == '__main__':
    logger.info("Iniciando servidor OCR API...")
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Servidor disponible en http://0.0.0.0:{port}")
    logger.info("Presiona Ctrl+C para detener el servidor")
    
    # Ejecutar servidor
    app.run(host='0.0.0.0', port=port, debug=False)
