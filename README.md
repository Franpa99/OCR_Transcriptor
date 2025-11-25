# OCR Transcriptor

Proyecto para digitalizar documentos escaneados mediante OCR automático con PaddleOCR.

---

## 📄 Descripción

Este script en Python toma imágenes escaneadas de documentos históricos, las procesa con técnicas avanzadas de preprocesamiento de imagen (mejora de contraste, corrección de rotación, binarización, reducción de ruido y nitidez configurable), y luego extrae el texto usando OCR con PaddleOCR.

El preprocesamiento es configurable para adaptarse a distintos tipos de documentos y calidades de escaneo. El resultado es un texto más limpio y preciso, facilitando la lectura, accesibilidad y análisis de documentos históricos o cualquier documentación impresa escaneada.

---

## 🧪 Cómo usarlo

1. Colocá las imágenes escaneadas dentro de una carpeta dentro de `image/`.
   Por ejemplo: `image/Documento1/`, `image/ArchivoX/`, etc.

2. (Opcional) Ajustá los parámetros en `config.py`:
   - Umbral de confianza del OCR
   - Parámetros de preprocesamiento (contraste, nitidez, etc.)
   - Activar/desactivar corrección ortográfica
   - Nivel de logging

3. Ejecutá el script `procesar_ocr.py` desde la consola:

   ```bash
   python procesar_ocr.py
   ```

4. El script procesará cada subcarpeta dentro de `image/`, escaneará las imágenes en orden alfabético y generará un archivo `.txt` con el mismo nombre de la carpeta dentro de `texto/`.

5. Las imágenes preprocesadas se guardan en la carpeta `procesadas/` para control y revisión.

6. Revisá el archivo `ocr_process.log` para ver detalles del procesamiento.

---

## 📦 Requisitos


- Python 3.x
- Instalar dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```

   O manualmente:

   ```bash
   pip install paddleocr opencv-python numpy pillow pyspellchecker
   ```

   (Recomendado: usar un entorno virtual)

---

## 📁 Estructura del proyecto

```
OCR_Transcriptor/
├── image/              # Carpeta con subcarpetas que contienen imágenes escaneadas
├── procesadas/         # Carpeta donde se guardan las imágenes preprocesadas
├── texto/              # Carpeta donde se guardan textos generados
├── backup/             # Carpeta con backups de imágenes/textos generados (no se sube al repo)
├── procesar_ocr.py     # Script principal en Python
├── config.py           # Archivo de configuración con parámetros ajustables
├── ocr_process.log     # Archivo de log del proceso (generado automáticamente)
├── requirements.txt    # Dependencias del proyecto
├── README.md           # Este archivo
└── .gitignore          # Archivos y carpetas ignoradas por git
```

---

## ✨ Características

- **Preprocesamiento avanzado**: Mejora de contraste, corrección de rotación, binarización, reducción de ruido, operaciones morfológicas (dilate/erode)
- **OCR en español**: Usa PaddleOCR optimizado para textos en español
- **Corrección ortográfica**: Corrección automática de palabras usando diccionario español
- **Limpieza de artefactos**: Elimina errores comunes del OCR (n0→no, rn→m, etc.)
- **Reconstrucción de palabras**: Une palabras partidas entre líneas
- **Dos versiones de salida**: 
  - **Versión RAW**: Texto crudo sin postprocesar
  - **Versión PROCESADA**: Texto limpiado y corregido
- **Perfiles configurables**: Optimizado para documentos modernos o históricos
- **Filtrado inteligente**: Elimina falsos positivos y texto con baja confianza
- **Logging detallado**: Archivo de log con información del proceso completo
- **Procesamiento por lotes**: Procesa múltiples carpetas automáticamente

---

## 🔧 Mejoras futuras

- Reconocimiento de columnas y tablas
- Interfaz web para validación colaborativa
- Parámetros de preprocesamiento ajustables desde línea de comandos
- Soporte para procesamiento paralelo de imágenes
- Métricas de calidad del OCR

---

## ⚖️ Licencia

Este proyecto está bajo la licencia MIT. 
Podés usarlo, modificarlo y compartirlo libremente.

---

## 👤 Autor

[@Franpa99](https://github.com/Franpa99)