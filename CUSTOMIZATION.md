# 🎨 Personalización de la Interfaz Web

Esta guía te ayuda a personalizar el diseño y funcionalidad de la interfaz web.

---

## 🖌️ Cambiar Colores

Edita `styles.css` - busca la sección `:root` al inicio del archivo:

```css
:root {
    --primary-color: #4f46e5;        /* Color principal (botones, enlaces) */
    --primary-hover: #4338ca;        /* Color al pasar el mouse */
    --success-color: #10b981;        /* Color de éxito */
    --error-color: #ef4444;          /* Color de error */
    --text-color: #1f2937;           /* Color del texto principal */
    --text-light: #6b7280;           /* Color del texto secundario */
    --background: #f9fafb;           /* Color de fondo de la página */
    --card-background: #ffffff;      /* Color de fondo de las tarjetas */
    --border-color: #e5e7eb;         /* Color de los bordes */
}
```

**Ejemplos de paletas:**

### Modo Oscuro
```css
:root {
    --primary-color: #818cf8;
    --primary-hover: #6366f1;
    --success-color: #34d399;
    --error-color: #f87171;
    --text-color: #f9fafb;
    --text-light: #d1d5db;
    --background: #111827;
    --card-background: #1f2937;
    --border-color: #374151;
}
```

### Verde Profesional
```css
:root {
    --primary-color: #059669;
    --primary-hover: #047857;
    --success-color: #10b981;
    --error-color: #dc2626;
    --text-color: #1f2937;
    --text-light: #6b7280;
    --background: #f0fdf4;
    --card-background: #ffffff;
    --border-color: #d1fae5;
}
```

### Azul Corporativo
```css
:root {
    --primary-color: #0284c7;
    --primary-hover: #0369a1;
    --success-color: #22c55e;
    --error-color: #ef4444;
    --text-color: #0f172a;
    --text-light: #64748b;
    --background: #f0f9ff;
    --card-background: #ffffff;
    --border-color: #bae6fd;
}
```

---

## 📝 Cambiar Textos

### Título y Subtítulo
Edita `index.html` - busca la sección `<header>`:

```html
<header>
    <h1>📄 Tu Título Aquí</h1>
    <p class="subtitle">Tu descripción aquí</p>
</header>
```

### Instrucciones del Drop Zone
Edita `index.html` - busca `<div class="drop-zone">`:

```html
<h3>Arrastra tus documentos aquí</h3>
<p>o haz clic para buscar en tu computadora</p>
```

### Enlaces del Footer
Edita `index.html` - busca `<footer>`:

```html
<footer>
    <p>Tu mensaje | 
        <a href="https://tu-github.com" target="_blank">GitHub</a> |
        <a href="mailto:tu@email.com">Contacto</a>
    </p>
</footer>
```

---

## 🔧 Configuración Avanzada

### Cambiar Límite de Tamaño de Archivo

**Backend (`app.py`):**
```python
MAX_FILE_SIZE = 20 * 1024 * 1024  # Cambiar 20 por el número de MB deseado
```

### Agregar Más Formatos de Archivo

**Backend (`app.py`):**
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp', 'gif'}
```

**Frontend (`index.html`):**
```html
<input type="file" id="fileInput" multiple 
       accept=".jpg,.jpeg,.png,.bmp,.tiff,.tif,.webp,.gif" hidden>
```

**Frontend (`script.js`):**
```javascript
const validExtensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif', 'webp', 'gif'];
```

### Cambiar Perfiles Disponibles

Edita `config.py` para crear nuevos perfiles:

```python
PERFILES = {
    "TU_PERFIL": {
        "ocr_language": "es",
        "confidence_threshold": 0.70,
        "min_text_length": 2,
        "preprocess": {
            'contrast_clip': 2.0,
            'binarize_block': 31,
            'binarize_C': 10,
            'denoise_h': 15,
            'sharpen': True,
            'deskew': True,
            'dilate_erode': False
        },
        "spell_check_enabled": True,
        "spell_check_language": "es",
        "generate_raw_output": False,
        "aggressive_cleaning": False
    }
}
```

Luego actualiza `index.html`:

```html
<select id="profile">
    <option value="TU_PERFIL">Tu perfil personalizado</option>
    <option value="HISTORICOS">Documentos históricos</option>
    <option value="ALTA_CALIDAD">Alta calidad</option>
</select>
```

---

## 🖼️ Agregar Logo

1. Guarda tu logo como `logo.png` en la carpeta raíz

2. Edita `index.html`:
```html
<header>
    <img src="logo.png" alt="Logo" style="max-width: 150px; margin-bottom: 1rem;">
    <h1>📄 OCR Transcriptor</h1>
    <p class="subtitle">Convierte imágenes de documentos en texto editable</p>
</header>
```

3. Ajusta estilos en `styles.css` si es necesario

---

## 📱 Personalizar Diseño Responsive

Edita la sección `@media` al final de `styles.css`:

```css
@media (max-width: 640px) {
    /* Tus ajustes para móviles */
    header h1 {
        font-size: 1.5rem;  /* Tamaño de título en móvil */
    }
}

@media (min-width: 1024px) {
    /* Tus ajustes para pantallas grandes */
    .container {
        max-width: 1200px;  /* Ancho máximo */
    }
}
```

---

## 🎯 Agregar Google Analytics

Agrega antes de cerrar `</head>` en `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=TU-ID-AQUI"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'TU-ID-AQUI');
</script>
```

---

## 🔔 Notificaciones Personalizadas

Reemplaza `alert()` en `script.js` con notificaciones elegantes:

### Opción 1: SweetAlert2
```html
<!-- En index.html, antes de script.js -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
```

```javascript
// En script.js, reemplazar alert() con:
Swal.fire('✅ Éxito', 'Texto copiado al portapapeles', 'success');
```

### Opción 2: Toastify
```html
<!-- En index.html -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css">
<script src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
```

```javascript
// En script.js:
Toastify({
    text: "✅ Texto copiado",
    duration: 3000,
    gravity: "top",
    position: "right",
    backgroundColor: "linear-gradient(to right, #10b981, #059669)",
}).showToast();
```

---

## 🌐 Agregar Más Idiomas

1. Crea archivos de traducción (`translations.js`):
```javascript
const translations = {
    es: {
        title: "OCR Transcriptor",
        subtitle: "Convierte imágenes de documentos en texto",
        dragDrop: "Arrastra tus imágenes aquí",
        // ... más textos
    },
    en: {
        title: "OCR Transcriptor",
        subtitle: "Convert document images to text",
        dragDrop: "Drag your images here",
        // ... más textos
    }
};
```

2. Agrega selector de idioma en `index.html`

3. Actualiza textos dinámicamente en `script.js`

---

## 💅 Agregar Animaciones

En `styles.css`:

```css
/* Animación al cargar */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.container {
    animation: fadeIn 0.5s ease-out;
}

/* Animación de botón */
.process-btn {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.process-btn:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 20px 40px rgba(79, 70, 229, 0.3);
}

/* Efecto de onda al hacer clic */
.process-btn:active {
    transform: scale(0.98);
}
```

---

## 📚 Recursos Adicionales

- [CSS Color Picker](https://htmlcolorcodes.com/)
- [Google Fonts](https://fonts.google.com/)
- [Hero Icons (SVG)](https://heroicons.com/)
- [Coolors - Paletas de colores](https://coolors.co/)
- [Animaciones CSS](https://animate.style/)

---

¡Personaliza tu OCR Transcriptor y hazlo único! 🎨✨
