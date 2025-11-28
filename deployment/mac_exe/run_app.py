import os
import sys
import uvicorn
import webbrowser
from threading import Timer
from pathlib import Path

# Configurar rutas para cuando se ejecuta como EXE o script
if getattr(sys, 'frozen', False):
    # Ejecutándose como PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Ejecutándose como script normal
    # Asumimos que este script está en deployment/mac_exe/ y el código en frontend/
    BASE_DIR = Path(__file__).resolve().parent.parent.parent / 'frontend'
    sys.path.append(str(BASE_DIR))

# --- IMPORTACIONES FORZADAS PARA PYINSTALLER ---
# PyInstaller a veces no detecta importaciones dinámicas (como las de Django).
# Al importarlas aquí dentro de un bloque 'if False', forzamos a que las incluya
# en el paquete final sin ejecutarlas realmente.
if False:
    import asonet_django.settings
    import asonet_django.urls
    import asonet_django.wsgi
    import django.core.management
    import django.db.migrations
    # Apps
    import core.apps
    import users.apps
    import socias.apps
    import finanzas.apps
    import eventos.apps
    import proyectos.apps
    import entidades.apps

def open_browser():
    """Abre el navegador automáticamente"""
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Establecer variable de entorno para configuración de Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asonet_django.settings")
    
    # Iniciar navegador tras una breve pausa
    Timer(1.5, open_browser).start()
    
    try:
        # Importar la aplicación ASGI directamente
        # Esto es necesario para que PyInstaller encuentre el módulo correctamente
        from asonet_django.asgi import application
        
        # Ejecutar migraciones automáticamente al inicio
        # Esto asegura que la DB tenga las tablas necesarias si es la primera ejecución
        print("Verificando estado de la base de datos...")
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        
        # Configuración del servidor
        config = uvicorn.Config(
            app=application,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        server.run()
        
    except Exception as e:
        # Loguear error a un archivo para depuración
        with open("error_log.txt", "w") as f:
            f.write(f"Error fatal: {e}\n")
            import traceback
            traceback.print_exc(file=f)
            
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")
