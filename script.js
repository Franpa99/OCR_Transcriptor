// Configuración de la API - Cambiar esta URL al desplegar el backend
const API_URL = 'http://localhost:5000';

// Estado de la aplicación
let selectedFiles = [];

// Elementos del DOM
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const processBtn = document.getElementById('processBtn');
const previewSection = document.getElementById('previewSection');
const fileList = document.getElementById('fileList');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const resultText = document.getElementById('resultText');
const errorText = document.getElementById('errorText');

// Eventos del drop zone
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// Manejar archivos seleccionados
function handleFiles(files) {
    const validExtensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'];
    
    Array.from(files).forEach(file => {
        const ext = file.name.split('.').pop().toLowerCase();
        if (validExtensions.includes(ext)) {
            // Evitar duplicados
            if (!selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        }
    });

    updateFileList();
    processBtn.disabled = selectedFiles.length === 0;
}

// Actualizar lista de archivos
function updateFileList() {
    if (selectedFiles.length === 0) {
        previewSection.style.display = 'none';
        return;
    }

    previewSection.style.display = 'block';
    fileList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>📄 ${file.name} (${formatFileSize(file.size)})</span>
            <button class="remove-file" onclick="removeFile(${index})">✕</button>
        `;
        fileList.appendChild(fileItem);
    });
}

// Remover archivo
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    processBtn.disabled = selectedFiles.length === 0;
}

// Formatear tamaño de archivo
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Procesar documentos
processBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    // Ocultar secciones y mostrar loading
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loadingSection.style.display = 'block';

    const formData = new FormData();
    
    // Agregar archivos
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });

    // Agregar configuración
    const profile = document.getElementById('profile').value;
    const language = document.getElementById('language').value;
    formData.append('profile', profile);
    formData.append('language', language);

    try {
        const response = await fetch(`${API_URL}/process`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        loadingSection.style.display = 'none';

        if (response.ok) {
            showResults(data.text, data.filename);
        } else {
            showError(data.error || 'Error al procesar los archivos');
        }
    } catch (error) {
        loadingSection.style.display = 'none';
        showError('No se pudo conectar con el servidor. Asegúrate de que el backend esté ejecutándose.');
        console.error('Error:', error);
    }
});

// Mostrar resultados
function showResults(text, filename) {
    resultsSection.style.display = 'block';
    resultText.textContent = text;

    // Configurar botón de copiar
    document.getElementById('copyBtn').onclick = () => {
        navigator.clipboard.writeText(text).then(() => {
            alert('✅ Texto copiado al portapapeles');
        });
    };

    // Configurar botón de descarga
    document.getElementById('downloadBtn').onclick = () => {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'transcripcion.txt';
        a.click();
        URL.revokeObjectURL(url);
    };

    // Configurar botón de nuevo proceso
    document.getElementById('newProcessBtn').onclick = resetApp;
}

// Mostrar error
function showError(message) {
    errorSection.style.display = 'block';
    errorText.textContent = message;

    document.getElementById('retryBtn').onclick = () => {
        errorSection.style.display = 'none';
        previewSection.style.display = selectedFiles.length > 0 ? 'block' : 'none';
    };
}

// Reiniciar aplicación
function resetApp() {
    selectedFiles = [];
    fileInput.value = '';
    updateFileList();
    processBtn.disabled = true;
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loadingSection.style.display = 'none';
}
