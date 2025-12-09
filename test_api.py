"""
Script de prueba simple para verificar que la API funciona
"""

import requests
import os

# URL del servidor (cambiar si es necesario)
API_URL = "http://localhost:5000"

def test_health():
    """Probar endpoint de salud"""
    print("🔍 Probando /health...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se pudo conectar al servidor: {e}")
        print("   ¿El servidor está ejecutándose? (python app.py)")
        return False

def test_profiles():
    """Probar endpoint de perfiles"""
    print("\n🔍 Probando /profiles...")
    try:
        response = requests.get(f"{API_URL}/profiles")
        if response.status_code == 200:
            profiles = response.json()
            print(f"✅ Perfiles disponibles: {list(profiles.keys())}")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_process():
    """Probar endpoint de procesamiento (requiere una imagen)"""
    print("\n🔍 Probando /process...")
    
    # Buscar una imagen de prueba
    test_image = None
    for root, dirs, files in os.walk("image"):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image = os.path.join(root, file)
                break
        if test_image:
            break
    
    if not test_image:
        print("⚠️  No se encontró ninguna imagen de prueba en la carpeta 'image/'")
        print("   Coloca una imagen en 'image/' para probar el procesamiento")
        return False
    
    print(f"   Usando imagen de prueba: {test_image}")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'files': f}
            data = {
                'profile': 'HISTORICOS',
                'language': 'es'
            }
            
            print("   Procesando... (esto puede tardar unos segundos)")
            response = requests.post(f"{API_URL}/process", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Procesamiento exitoso")
                print(f"   Archivos procesados: {result.get('files_processed', 0)}")
                print(f"   Caracteres extraídos: {len(result.get('text', ''))}")
                print(f"   Primeros 100 caracteres:")
                print(f"   {result.get('text', '')[:100]}...")
                return True
            else:
                print(f"❌ Error: Status code {response.status_code}")
                print(f"   Mensaje: {response.json()}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("  OCR Transcriptor - Test de API")
    print("=" * 60)
    print()
    
    # Ejecutar tests
    health_ok = test_health()
    
    if health_ok:
        test_profiles()
        test_process()
    
    print("\n" + "=" * 60)
    print("  Tests completados")
    print("=" * 60)

if __name__ == "__main__":
    main()
