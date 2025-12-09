# 🚀 Inicio Rápido - Interfaz Web

## Opción 1: Prueba Local (5 minutos)

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar el servidor
**Windows:**
```bash
start_server.bat
```

**Mac/Linux:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**O manualmente:**
```bash
python app.py
```

### 3. Abrir la interfaz
- Abre `index.html` en tu navegador
- O ve a `http://localhost:5000` (si implementas la ruta principal)

### 4. ¡Listo! 🎉
Arrastra imágenes y procesa documentos.

---

## Opción 2: Despliegue en Producción

### GitHub Pages (Frontend)
1. Sube los archivos al repositorio
2. Ve a Settings → Pages
3. Activa GitHub Pages desde la rama `main`
4. Tu sitio estará en: `https://tu-usuario.github.io/OCR_Transcriptor/`

### Render.com (Backend - Gratis)
1. Crea cuenta en [Render.com](https://render.com)
2. New → Web Service
3. Conecta tu repositorio GitHub
4. Render detectará automáticamente la configuración
5. Deploy! ⏱️ (tarda 5-10 min)

### Conectar Frontend con Backend
1. Copia la URL de tu backend en Render
   - Ejemplo: `https://ocr-transcriptor-api.onrender.com`
2. Edita `script.js` línea 2:
   ```javascript
   const API_URL = 'https://tu-backend.onrender.com';
   ```
3. Commit y push

**📘 [Guía completa de despliegue](DEPLOY.md)**

---

## ⚡ Solución Rápida de Problemas

### "No se pudo conectar con el servidor"
✅ Verifica que `python app.py` esté ejecutándose
✅ Revisa la URL en `script.js`

### "Error al procesar archivos"
✅ Formatos soportados: JPG, PNG, BMP, TIFF
✅ Tamaño máximo: 20MB por archivo

### Backend lento en Render
⏰ Primera petición tarda 30-60s (servicio gratuito se duerme)
✅ Peticiones siguientes son rápidas

---

## 📖 Más información

- [README completo](README.md)
- [Guía de despliegue detallada](DEPLOY.md)
- [Guía de inicio](GUIA_INICIO.md)

---

¡Disfruta digitalizando tus documentos! 📄✨
