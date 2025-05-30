# OCR Luisa

Proyecto para digitalizar documentos escaneados del proyecto Luisa (UDELAR) mediante OCR automático.

---

## Descripción

Este script en Python toma imágenes escaneadas de documentos históricos, las procesa con técnicas de preprocesamiento de imagen y OCR usando EasyOCR, y genera archivos de texto con el contenido digitalizado.

Está pensado para facilitar la lectura, accesibilidad y análisis de documentos de la dictadura.

---

## Cómo usarlo

1. Colocá las imágenes escaneadas dentro de la carpeta `image/`
2. Ejecutá el script `procesar_ocr.py` desde la consola:

   ```bash
   python procesar_ocr.py
   ```

3. Los archivos de texto resultantes se guardarán en la carpeta `texto/`

---

## Requisitos

- Python 3.x
- Paquetes necesarios (se pueden instalar con pip):

  ```bash
  pip install easyocr opencv-python spellchecker torch
  ```

---

## Estructura del proyecto

```
OCR_Luisa/
├── image/              # Carpeta con imágenes escaneadas
├── texto/              # Carpeta donde se guardan textos generados
├── procesar_ocr.py     # Script principal en Python
├── README.md           # Este archivo
└── .gitignore          # Archivos y carpetas ignoradas por git
```

---

## Mejoras futuras

- Mejor reconocimiento de columnas y formatos
- Procesamiento multilenguaje
- Corrección ortográfica avanzada
- Interfaz web para validación colaborativa

---

## Licencia

Este proyecto está bajo la licencia MIT.  
Podés usarlo, modificarlo y compartirlo libremente.

---

## Autor

@TuUsuario
