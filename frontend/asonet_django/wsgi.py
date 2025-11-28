"""
WSGI config for asonet_django project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from a2wsgi import ASGIMiddleware

# Configuración de rutas para encontrar el backend
# frontend/asonet_django/wsgi.py -> frontend/asonet_django -> frontend -> root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"

# Añadir backend al path
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')

# Aplicación Django
django_app = get_wsgi_application()

# Intentar importar y montar FastAPI
try:
    from app.main import app as fastapi_app
    fastapi_wsgi = ASGIMiddleware(fastapi_app)

    # Montar FastAPI en /api
    application = DispatcherMiddleware(django_app, {
        '/api': fastapi_wsgi
    })
    print("FastAPI mounted successfully at /api")
except ImportError as e:
    print(f"Warning: Could not import FastAPI app: {e}")
    print(f"Sys path: {sys.path}")
    application = django_app
