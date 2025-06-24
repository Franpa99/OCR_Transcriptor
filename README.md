# OCR Transcriptor

Proyecto para digitalizar documentos escaneados mediante OCR automático con PaddleOCR.

---

## Descripción

Este script en Python toma imágenes escaneadas de documentos históricos, las procesa con técnicas de preprocesamiento de imagen para mejorar la calidad, y luego extrae el texto usando OCR con PaddleOCR.

Está pensado para facilitar la lectura, accesibilidad y análisis de documentos de la dictadura uruguaya o cualquier documentación impresa escaneada.

---

## Cómo usarlo

1. Colocá las imágenes escaneadas dentro de una carpeta dentro de `image/`. Por ejemplo: `image/Documento1/`, `image/ArchivoX/`, etc.

2. Ejecutá el script `procesar_ocr.py` desde la consola:

   ```bash
   python procesar_ocr.py
   ```

3. El script procesará cada carpeta dentro de `image/`, escaneará las imágenes en orden alfabético y generará un archivo de texto con el mismo nombre de la carpeta dentro de la carpeta `texto/`.

4. Las imágenes procesadas con el preprocesamiento se guardan en la carpeta `procesadas/` para referencia y revisión.

---

## Requisitos

- Python 3.x
- Paquetes necesarios (se pueden instalar con pip):

  ```bash
  pip install paddleocr opencv-python numpy pillow
  ```

---

## Estructura del proyecto

```
OCR_Transcriptor/
├── image/              # Carpeta con subcarpetas que contienen imágenes escaneadas
├── procesadas/         # Carpeta donde se guardan las imágenes preprocesadas
├── texto/              # Carpeta donde se guardan textos generados
├── procesar_ocr.py     # Script principal en Python
├── README.md           # Este archivo
└── .gitignore          # Archivos y carpetas ignoradas por git
```

---

## Mejoras futuras

- Mejor reconocimiento de columnas y formatos
- Corrección ortográfica avanzada
- Interfaz web para validación colaborativa

---

## Licencia

Este proyecto está bajo la licencia MIT.  
Podés usarlo, modificarlo y compartirlo libremente.

---

## Autor

@Franpa99
