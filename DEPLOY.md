# 🌐 Guía de Despliegue Web

Esta guía explica cómo desplegar la interfaz web del OCR Transcriptor usando GitHub Pages para el frontend y diferentes opciones para el backend.

---

## 📋 Tabla de Contenidos

1. [Despliegue del Frontend (GitHub Pages)](#despliegue-del-frontend)
2. [Despliegue del Backend](#despliegue-del-backend)
3. [Prueba Local](#prueba-local)
4. [Solución de Problemas](#solución-de-problemas)

---

## 🎨 Despliegue del Frontend

### Opción 1: GitHub Pages (Recomendado)

1. **Preparar el repositorio:**
   ```bash
   git add index.html styles.css script.js
   git commit -m "Add web interface"
   git push origin main
   ```

2. **Activar GitHub Pages:**
   - Ve a tu repositorio en GitHub
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`, folder: `/ (root)`
   - Save

3. **Configurar la URL del backend:**
   - Edita `script.js`
   - Cambia `const API_URL = 'http://localhost:5000'` por la URL de tu backend desplegado
   - Ejemplo: `const API_URL = 'https://tu-backend.onrender.com'`

4. **Tu sitio estará disponible en:**
   ```
   https://franpa99.github.io/OCR_Transcriptor/
   ```

---

## 🖥️ Despliegue del Backend

El backend necesita ejecutarse en un servidor porque procesa imágenes con Python. Aquí hay varias opciones:

### Opción 1: Render.com (Gratis, Recomendado)

1. **Crear cuenta en [Render.com](https://render.com)**

2. **Crear un Web Service:**
   - New → Web Service
   - Conecta tu repositorio de GitHub
   - Configuración:
     - Name: `ocr-transcriptor-api`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app.py`
     - Instance Type: `Free`

3. **Esperar el despliegue** (5-10 minutos la primera vez)

4. **Copiar la URL** (ej: `https://ocr-transcriptor-api.onrender.com`)

5. **Actualizar script.js** con la nueva URL

**Nota:** El plan gratuito de Render se duerme después de 15 minutos de inactividad. La primera petición puede tardar 30-60 segundos.

### Opción 2: Railway.app (Gratis con límites)

1. **Crear cuenta en [Railway.app](https://railway.app)**

2. **Deploy from GitHub:**
   - New Project → Deploy from GitHub
   - Selecciona tu repositorio
   - Railway detectará automáticamente Python

3. **Variables de entorno:**
   - No se requieren adicionales

4. **Obtener URL pública:**
   - Settings → Generate Domain
   - Copiar la URL

### Opción 3: PythonAnywhere (Gratis)

1. **Crear cuenta en [PythonAnywhere](https://www.pythonanywhere.com)**

2. **Subir código:**
   - Files → Upload files
   - Sube todos los archivos .py y requirements.txt

3. **Crear Web App:**
   - Web → Add a new web app
   - Framework: Flask
   - Python version: 3.10

4. **Configurar WSGI:**
   ```python
   import sys
   path = '/home/tuusuario/OCR_Transcriptor'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

5. **Instalar dependencias:**
   ```bash
   pip install --user -r requirements.txt
   ```

### Opción 4: Servidor Propio/VPS

Si tienes un servidor propio:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar con Gunicorn (producción)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# O con el servidor de desarrollo (solo para pruebas)
python app.py
```

**Configurar NGINX como proxy inverso:**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Prueba Local

Antes de desplegar, prueba todo localmente:

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Iniciar el backend:**
   ```bash
   python app.py
   ```
   
   Deberías ver:
   ```
   Iniciando servidor OCR API...
   Servidor disponible en http://localhost:5000
   ```

3. **Abrir el frontend:**
   - Opción A: Abre `index.html` directamente en tu navegador
   - Opción B: Usa un servidor local:
     ```bash
     # Python
     python -m http.server 8000
     
     # O Node.js
     npx http-server
     ```
   - Ve a `http://localhost:8000`

4. **Probar la funcionalidad:**
   - Arrastra una imagen al área de carga
   - Selecciona el perfil y idioma
   - Haz clic en "Procesar Documentos"
   - Verifica que aparece la transcripción

---

## 🐛 Solución de Problemas

### Error: "No se pudo conectar con el servidor"

**Causa:** El backend no está ejecutándose o la URL es incorrecta.

**Solución:**
1. Verifica que el backend esté corriendo
2. Revisa la URL en `script.js` línea 2
3. Comprueba que no haya errores en la consola del navegador (F12)

### Error: CORS

**Causa:** El backend no permite peticiones desde el frontend.

**Solución:** El código ya incluye `flask-cors`, pero si persiste:
```python
# En app.py
CORS(app, resources={r"/*": {"origins": "https://franpa99.github.io"}})
```

### Backend muy lento en Render

**Causa:** El servicio gratuito se duerme después de inactividad.

**Solución:**
1. Primera petición será lenta (30-60s)
2. Considera el plan de pago ($7/mes)
3. O usa otro servicio

### Imágenes muy grandes

**Causa:** El límite es 20MB por archivo.

**Solución:**
1. Comprime las imágenes antes de subir
2. O aumenta `MAX_FILE_SIZE` en `app.py` línea 32

### Error al procesar algunos archivos

**Causa:** Formato de imagen no soportado o corrupto.

**Solución:**
1. Verifica que el formato sea JPG, PNG, BMP o TIFF
2. Prueba abrir la imagen en otro programa primero
3. Revisa los logs del servidor

---

## 📊 Arquitectura del Sistema

```
┌─────────────────┐
│  GitHub Pages   │  ← Frontend estático (HTML/CSS/JS)
│  (Frontend)     │
└────────┬────────┘
         │
         │ HTTPS
         │
         ▼
┌─────────────────┐
│  Render/Railway │  ← Backend Python (Flask + PaddleOCR)
│  (Backend API)  │
└─────────────────┘
```

**Flujo de trabajo:**
1. Usuario sube imagen en el frontend
2. Frontend envía imagen al backend vía API
3. Backend procesa con OCR
4. Backend devuelve texto
5. Frontend muestra resultado

---

## 🔐 Consideraciones de Seguridad

- **Límite de tamaño:** Los archivos están limitados a 20MB
- **Validación de archivos:** Solo se aceptan formatos de imagen válidos
- **Archivos temporales:** Se eliminan después del procesamiento
- **CORS:** Configurado para aceptar peticiones solo desde dominios específicos

---

## 💡 Próximos Pasos

1. ✅ Despliega el frontend en GitHub Pages
2. ✅ Despliega el backend en Render/Railway
3. ✅ Actualiza la URL en `script.js`
4. ✅ Prueba con documentos reales
5. 📊 (Opcional) Añade Google Analytics para estadísticas
6. 🎨 (Opcional) Personaliza el diseño en `styles.css`

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs del backend
2. Abre las Developer Tools del navegador (F12) → Console
3. Crea un issue en GitHub con:
   - Descripción del problema
   - Logs del backend
   - Errores de la consola del navegador
   - Navegador y sistema operativo

---

¡Listo! Tu OCR Transcriptor está ahora disponible en la web. 🎉
