import os
import sys
from pathlib import Path

# 1. Configuración de Rutas
# Obtenemos la ruta base del proyecto (donde está este archivo)
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

# Añadir al path para que Python encuentre los módulos
sys.path.append(str(BASE_DIR))
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(FRONTEND_DIR))

# 2. Configuración de Django (Frontend)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asonet_django.settings")

import django
django.setup()
from django.core.wsgi import get_wsgi_application

# Aplicación WSGI de Django
django_app = get_wsgi_application()

# 3. Configuración de FastAPI (Backend)
from app.main import app as fastapi_app
from a2wsgi import ASGIMiddleware

# Convertir FastAPI (ASGI) a WSGI usando a2wsgi
fastapi_wsgi_app = ASGIMiddleware(fastapi_app)

# 4. Unificación (Dispatcher)
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
