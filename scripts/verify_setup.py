#!/usr/bin/env python3
"""
Script de verificación de configuración
Valida que todo esté listo antes de ejecutar
"""

import os
import sys
import yaml
import requests

def print_header(text):
    """Imprime header bonito"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    """Verifica versión de Python"""
    print("\n🐍 Verificando Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requiere 3.8+)")
        return False

def check_dependencies():
    """Verifica dependencias instaladas"""
    print("\n📦 Verificando dependencias...")
    required = ['requests', 'yaml', 'icalendar', 'pytz']
    missing = []
    
    for module in required:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (faltante)")
            missing.append(module)
    
    if missing:
        print(f"\n   💡 Instala con: pip3 install {' '.join(missing)}")
        return False
    return True

def check_config():
    """Verifica archivo de configuración"""
    print("\n⚙️  Verificando configuración...")
    config_path = 'config/config.yaml'

    if not os.path.exists(config_path):
        print("   ❌ config.yaml no encontrado")
        return False, None
    
    print("   ✅ config.yaml existe")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("   ✅ config.yaml válido")
        return True, config
    except Exception as e:
        print(f"   ❌ Error leyendo config.yaml: {e}")
        return False, None

def check_hubspot_api(api_key):
    """Verifica conexión con HubSpot"""
    print("\n🔌 Verificando HubSpot API...")
    
    if api_key == "TU_API_KEY_AQUI":
        print("   ⚠️  API key no configurada")
        print("   💡 Edita config/config.yaml y reemplaza TU_API_KEY_AQUI")
        return False
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(
            "https://api.hubapi.com/crm/v3/objects/contacts?limit=1",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Conexión exitosa con HubSpot")
            return True
        elif response.status_code == 401:
            print("   ❌ API key inválida")
            return False
        else:
            print(f"   ❌ Error {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def check_calendar(ical_url):
    """Verifica acceso al calendario"""
    print("\n📅 Verificando Google Calendar...")
    
    try:
        response = requests.get(ical_url, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Calendar público accesible")
            
            # Verificar que sea un iCal válido
            if 'BEGIN:VCALENDAR' in response.text:
                print("   ✅ Formato iCal válido")
                return True
            else:
                print("   ❌ No es un archivo iCal válido")
                return False
        else:
            print(f"   ❌ Error {response.status_code} accediendo al calendar")
            print("   💡 Verifica que el calendario sea público")
            return False
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def check_directories():
    """Verifica estructura de directorios"""
    print("\n📁 Verificando directorios...")

    dirs = ['logs', 'data', 'scripts', 'config']

    all_ok = True
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ⚠️  {dir_name}/ (creando...)")
            os.makedirs(dir_name, exist_ok=True)

    return True

def main():
    print_header("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
    
    checks = []
    
    # Python
    checks.append(('Python 3.8+', check_python()))
    
    # Dependencias
    checks.append(('Dependencias', check_dependencies()))
    
    # Config file
    config_ok, config = check_config()
    checks.append(('Config file', config_ok))
    
    # HubSpot API
    if config_ok and config:
        api_key = config.get('hubspot', {}).get('api_key', 'TU_API_KEY_AQUI')
        checks.append(('HubSpot API', check_hubspot_api(api_key)))
        
        # Calendar
        ical_url = config.get('google_calendar', {}).get('ical_url', '')
        checks.append(('Google Calendar', check_calendar(ical_url)))
    else:
        checks.append(('HubSpot API', False))
        checks.append(('Google Calendar', False))
    
    # Directorios
    checks.append(('Directorios', check_directories()))
    
    # Resumen
    print_header("📊 RESUMEN")
    
    all_ok = all(check[1] for check in checks)
    
    for name, status in checks:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}")
    
    print("\n" + "="*60)
    
    if all_ok:
        print("✅ TODO LISTO PARA EJECUTAR")
        print("\n📝 Próximo paso:")
        print("   python3 scripts/main_extractor.py")
    else:
        print("⚠️  CONFIGURACIÓN INCOMPLETA")
        print("\n📝 Revisa los items marcados con ❌")
        print("📖 Consulta: QUICKSTART.md o README.md")
    
    print("="*60)

if __name__ == "__main__":
    main()
