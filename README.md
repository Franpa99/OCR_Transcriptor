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

2. Ejecutá el script `procesar_ocr.py` desde la consola:

   ```bash
   python procesar_ocr.py
   ```

   Si querés ajustar los parámetros de preprocesamiento (contraste, binarización, nitidez, etc.), modificá los valores en la función `preprocess_image` dentro del script.

3. El script procesará cada subcarpeta dentro de `image/`, escaneará las imágenes en orden alfabético y generará un archivo `.txt` con el mismo nombre de la carpeta dentro de `texto/`.

4. Las imágenes preprocesadas se guardan en la carpeta `procesadas/` para control y revisión.

---

## 📦 Requisitos


- Python 3.x
- Instalar dependencias necesarias:

   ```bash
   pip install paddleocr opencv-python numpy pillow
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
├── README.md           # Este archivo
└── .gitignore          # Archivos y carpetas ignoradas por git
```

---

## 🔧 Mejoras futuras

- Reconocimiento de columnas y tablas
- Corrección ortográfica automática
- Interfaz web para validación colaborativa
- Parámetros de preprocesamiento ajustables desde línea de comandos
- Mejor filtrado de falsos positivos en OCR

---

## ⚖️ Licencia

Este proyecto está bajo la licencia MIT. 
Podés usarlo, modificarlo y compartirlo libremente.

---

## 👤 Autor

[@Franpa99](https://github.com/Franpa99)