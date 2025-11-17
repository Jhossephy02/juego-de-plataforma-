# setup.py - Script de configuración e instalación automática

import os
import sys
import subprocess
import platform

def print_banner():
    """Muestra banner de bienvenida"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           🎮 RAYMAN SHINOBI - MUSIC RUNNER 🎵             ║
║                                                            ║
║                Setup & Installation Script                 ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Verifica que Python sea 3.8+"""
    print("🐍 Verificando versión de Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Tu versión: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detectado")

def create_directories():
    """Crea estructura de directorios necesaria"""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        'assets/music',
        'assets/player/idle',
        'assets/player/run',
        'assets/player/jump',
        'assets/obstacles',
        'assets/powerups',
        'assets/world/layers/sky',
        'assets/world/layers/mountains',
        'assets/world/layers/mid',
        'assets/world/layers/foreground',
        'assets/ui',
        'data/cache',
        'logs',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ Estructura de directorios creada")

def install_dependencies():
    """Instala dependencias de requirements.txt"""
    print("\n📦 Instalando dependencias...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ Error: requirements.txt no encontrado")
        return False
    
    try:
        # Actualizar pip
        print("   Actualizando pip...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ])
        
        # Instalar dependencias
        print("   Instalando paquetes...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def check_system_dependencies():
    """Verifica dependencias del sistema según OS"""
    print("\n🖥️  Verificando dependencias del sistema...")
    
    system = platform.system()
    
    if system == 'Windows':
        print("   📌 Windows detectado")
        print("   ⚠️  Asegúrate de tener instalado:")
        print("      - Microsoft Visual C++ 14.0+")
        print("      - DirectX 9.0c+")
        print("   📥 Descarga desde:")
        print("      https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    
    elif system == 'Linux':
        print("   📌 Linux detectado")
        print("   ⚠️  Ejecuta estos comandos si tienes problemas:")
        print("      sudo apt-get install python3-dev libasound2-dev")
        print("      sudo apt-get install libportaudio2 libsndfile1")
    
    elif system == 'Darwin':  # macOS
        print("   📌 macOS detectado")
        print("   ⚠️  Si tienes problemas, instala:")
        print("      brew install portaudio")
    
    print("✅ Verificación del sistema completada")

def create_sample_music_info():
    """Crea archivo de información sobre música"""
    print("\n🎵 Creando guía de música...")
    
    info_path = 'assets/music/README.txt'
    
    content = """
╔════════════════════════════════════════════════════════════╗
║          GUÍA PARA AGREGAR MÚSICA AL JUEGO                ║
╚════════════════════════════════════════════════════════════╝

1. FORMATOS SOPORTADOS:
   ✅ MP3 (.mp3)
   ✅ WAV (.wav)
   ✅ OGG (.ogg)
   ✅ FLAC (.flac)

2. CÓMO AGREGAR MÚSICA:
   - Coloca tus archivos de música en esta carpeta
   - El juego los detectará automáticamente
   - Aparecerán en el selector de música

3. RECOMENDACIONES:
   ✨ Música con beats marcados (EDM, Rock, Hip-Hop)
   ✨ Canciones de 2-5 minutos
   ✨ Archivos MP3 para carga más rápida
   ✨ Evita música muy lenta o ambiental

4. EJEMPLOS DE BUENA MÚSICA:
   - Soundtracks de videojuegos
   - Música electrónica/EDM
   - Rock/Metal con ritmo constante
   - Música chiptune/8-bit

5. FUENTES DE MÚSICA LIBRE:
   - https://freemusicarchive.org
   - https://incompetech.com
   - https://bensound.com
   - https://ccmixter.org

¡Disfruta del juego! 🎮
"""
    
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Guía creada en: {info_path}")

def verify_installation():
    """Verifica que todo esté instalado correctamente"""
    print("\n🔍 Verificando instalación...")
    
    try:
        import pygame
        print(f"   ✅ Pygame {pygame.version.ver}")
    except ImportError:
        print("   ❌ Pygame no instalado")
        return False
    
    try:
        import librosa
        print(f"   ✅ Librosa {librosa.__version__}")
    except ImportError:
        print("   ❌ Librosa no instalado")
        return False
    
    try:
        import numpy
        print(f"   ✅ NumPy {numpy.__version__}")
    except ImportError:
        print("   ❌ NumPy no instalado")
        return False
    
    print("✅ Instalación verificada correctamente")
    return True

def create_run_script():
    """Crea script de ejecución rápida"""
    print("\n🚀 Creando scripts de ejecución...")
    
    # Script para Windows
    if platform.system() == 'Windows':
        with open('run_game.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Rayman Shinobi...\n')
            f.write('python -m src.main\n')
            f.write('pause\n')
        print("   ✅ run_game.bat creado")
    
    # Script para Linux/Mac
    else:
        with open('run_game.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Rayman Shinobi..."\n')
            f.write('python -m src.main\n')
        
        # Hacer ejecutable
        os.chmod('run_game.sh', 0o755)
        print("   ✅ run_game.sh creado")

def print_next_steps():
    """Muestra los siguientes pasos"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                    ✅ INSTALACIÓN COMPLETA                 ║
╚════════════════════════════════════════════════════════════╝

📝 PRÓXIMOS PASOS:

1. 🎵 Agregar Música:
   - Coloca archivos de música en: assets/music/
   - Formatos: MP3, WAV, OGG, FLAC

2. 🎨 Assets Visuales (opcional):
   - Agrega sprites en assets/player/
   - Agrega fondos en assets/world/layers/
   - El juego funciona sin assets con placeholders

3. 🚀 Ejecutar el Juego:
   Windows: run_game.bat
   Linux/Mac: ./run_game.sh
   O directamente: python -m src.main

4. 📚 Documentación:
   - README.md - Guía completa
   - ESPECIFICACIONES_TECNICAS.md - Detalles técnicos
   - MEJORAS_FUTURAS.md - Roadmap

💡 TIPS:
   - Lee el README.md para más información
   - Revisa assets/music/README.txt para guía de música
   - El análisis musical puede tomar 5-10 segundos por canción

🎮 ¡LISTO PARA JUGAR!
   Ejecuta el juego y selecciona tu música favorita

""")

def main():
    """Función principal del setup"""
    print_banner()
    
    try:
        # Verificaciones
        check_python_version()
        
        # Crear estructura
        create_directories()
        
        # Instalar dependencias
        if not install_dependencies():
            print("\n⚠️  Algunas dependencias no se instalaron correctamente")
            print("   Intenta instalarlas manualmente:")
            print("   pip install -r requirements.txt")
            return
        
        # Verificar sistema
        check_system_dependencies()
        
        # Crear archivos auxiliares
        create_sample_music_info()
        
        # Verificar instalación
        if not verify_installation():
            print("\n⚠️  La instalación no se completó correctamente")
            return
        
        # Crear scripts de ejecución
        create_run_script()
        
        # Mostrar siguientes pasos
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante la instalación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()