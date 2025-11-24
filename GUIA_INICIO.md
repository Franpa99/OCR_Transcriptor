# Guía de Inicio Rápido - OCR Transcriptor

## Instalación

1. **Clonar o descargar el repositorio**

2. **Crear un entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Estructura de Carpetas

Antes de ejecutar el script, asegurate de tener esta estructura:

```
OCR_Transcriptor/
├── image/
│   ├── MiDocumento1/
│   │   ├── pagina1.jpg
│   │   ├── pagina2.jpg
│   │   └── pagina3.jpg
│   └── MiDocumento2/
│       ├── scan1.png
│       └── scan2.png
└── ...
```

## Uso Básico

1. **Colocar imágenes**: Creá una carpeta dentro de `image/` (ej: `image/MiDocumento/`) y colocá tus imágenes ahí.

2. **Ejecutar**: `python procesar_ocr.py`

3. **Ver resultados**: 
   - Texto extraído: `texto/MiDocumento.txt`
   - Imágenes procesadas: `procesadas/`
   - Log del proceso: `ocr_process.log`

## Configuración Avanzada

Editá `config.py` para ajustar:

### Parámetros de OCR
```python
CONFIDENCE_THRESHOLD = 0.7  # Menor = más texto (pero más errores)
                            # Mayor = menos texto (pero más preciso)
```

### Preprocesamiento de Imagen
```python
PREPROCESS_CONFIG = {
    'contrast_clip': 2.0,      # Contraste (1.0-4.0, mayor = más contraste)
    'binarize_block': 31,      # Tamaño ventana para binarización (impar)
    'binarize_C': 10,          # Ajuste fino de binarización
    'denoise_h': 20,           # Reducción de ruido (10-30 recomendado)
    'sharpen': True            # Aplicar filtro de nitidez
}
```

### Corrección Ortográfica
```python
SPELL_CHECK_ENABLED = True   # Activar/desactivar corrección
```

### Logging
```python
LOG_LEVEL = 'INFO'  # Opciones: DEBUG, INFO, WARNING, ERROR
```

## Consejos para Mejores Resultados

1. **Calidad de imagen**: Usá imágenes con al menos 300 DPI
2. **Contraste**: Documentos con buen contraste funcionan mejor
3. **Rotación**: El script corrige rotación automáticamente
4. **Idioma**: Por defecto usa español, cambiar en `config.py` si es necesario
5. **Prueba y ajusta**: Si los resultados no son buenos, ajustá parámetros en `config.py`

## Resolución de Problemas

### Error al instalar PaddleOCR
```bash
# Instalá las dependencias del sistema primero
pip install --upgrade pip
pip install paddlepaddle
pip install paddleocr
```

### Texto no detectado o erróneo
- Bajá `CONFIDENCE_THRESHOLD` en `config.py`
- Ajustá parámetros de preprocesamiento
- Verificá la calidad de las imágenes de entrada

### Proceso muy lento
- Procesá menos imágenes a la vez
- Considerá usar una máquina con GPU

## Ejemplos de Uso

### Procesar documentos históricos con mucho ruido
```python
# En config.py
PREPROCESS_CONFIG = {
    'contrast_clip': 3.0,      # Mayor contraste
    'denoise_h': 30,           # Mayor reducción de ruido
    'sharpen': True
}
CONFIDENCE_THRESHOLD = 0.6     # Aceptar más texto
```

### Procesar documentos modernos de alta calidad
```python
# En config.py
PREPROCESS_CONFIG = {
    'contrast_clip': 1.5,      # Menos procesamiento
    'denoise_h': 10,           
    'sharpen': False           # No necesario
}
CONFIDENCE_THRESHOLD = 0.8     # Solo texto muy confiable
```

## Soporte

Si encontrás problemas, revisá:
1. El archivo `ocr_process.log` para detalles
2. La carpeta `procesadas/` para ver cómo quedaron las imágenes
3. Issues en GitHub para problemas conocidos
