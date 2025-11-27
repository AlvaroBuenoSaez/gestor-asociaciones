import os
import sys

# --- 1. Configuración de Rutas ---
# IMPORTANTE: En PythonAnywhere, este archivo vive en /var/www, por lo que __file__ no sirve para localizar tu código.
# Debemos apuntar explícitamente a la carpeta donde clonaste el repo.

# Detectamos el directorio home del usuario (ej: /home/AlvaroBueno)
HOME_DIR = os.path.expanduser("~")
PROJECT_NAME = "gestor-asociaciones" # Asegúrate de que tu carpeta se llama así

BASE_DIR = os.path.join(HOME_DIR, PROJECT_NAME)
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Añadir al path para que Python encuentre los módulos
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)
if FRONTEND_DIR not in sys.path:
    sys.path.append(FRONTEND_DIR)

# --- 2. Configuración de Django (Frontend) ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asonet_django.settings")

import django
django.setup()
from django.core.wsgi import get_wsgi_application

# Aplicación WSGI de Django
django_app = get_wsgi_application()

# --- 3. Configuración de FastAPI (Backend) ---
from app.main import app as fastapi_app
from a2wsgi import ASGIMiddleware

# Convertir FastAPI (ASGI) a WSGI usando a2wsgi
# Esto es necesario porque PythonAnywhere usa WSGI
fastapi_wsgi_app = ASGIMiddleware(fastapi_app)

# --- 4. Unificación (Dispatcher) ---
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Montar las aplicaciones:
# - /api -> FastAPI
# - /    -> Django (por defecto)
application = DispatcherMiddleware(
    django_app,
    {
        "/api": fastapi_wsgi_app
    }
)
