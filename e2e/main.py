import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope, Receive, Send

# --- Configuration Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

# Add to sys.path so imports work
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(FRONTEND_DIR))

# --- Setup Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
import django
django.setup()
from django.core.asgi import get_asgi_application
from django.conf import settings

django_app = get_asgi_application()

# --- Setup FastAPI ---
from app.main import app as fastapi_app

# --- Setup Static Files ---
# We need to serve static files because Django ASGI doesn't do it automatically in this mode
static_app = StaticFiles(directory=str(FRONTEND_DIR / "static"))

# --- Main Dispatcher ---
async def app(scope: Scope, receive: Receive, send: Send):
    if scope["type"] == "http":
        path = scope["path"]
        
        # 1. API & Docs -> FastAPI
        if path.startswith("/api") or path.startswith("/health") or path.startswith("/docs") or path.startswith("/openapi.json"):
            await fastapi_app(scope, receive, send)
            return

        # 2. Static Files -> StaticFiles app
        if path.startswith("/static"):
            # Strip /static prefix for the StaticFiles app? 
            # StaticFiles mounts usually expect the prefix to be stripped if mounted, 
            # but here we are calling it directly. 
            # Let's check if we can just mount it in a Starlette app wrapper, 
            # but we are writing a raw ASGI function.
            # Easier: Use Starlette's Mount if we were building a Starlette app, 
            # but we want a custom dispatch.
            
            # Let's use a helper app for static
            # We need to adjust the scope path for StaticFiles if it expects root-relative paths
            # But StaticFiles(directory=...) serves files relative to that directory.
            # If request is /static/css/style.css, we want to serve css/style.css from directory.
            # So we should strip /static.
            
            # Clone scope to not mutate original
            scope_copy = dict(scope)
            scope_copy["path"] = path[len("/static"):]
            await static_app(scope_copy, receive, send)
            return

        # 3. Everything else -> Django
        await django_app(scope, receive, send)
        return

    # Lifespan and other protocols
    if scope["type"] == "lifespan":
        # We can just pass lifespan to FastAPI as it handles startup/shutdown
        await fastapi_app(scope, receive, send)
        return

    # WebSocket?
    # If Django uses channels, it might need websocket. 
    # If FastAPI uses websockets, it needs it.
    # For now, let's assume websockets go to Django if not /api?
    # Or just default to Django.
    await django_app(scope, receive, send)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting E2E Server (Django + FastAPI) on port 8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
