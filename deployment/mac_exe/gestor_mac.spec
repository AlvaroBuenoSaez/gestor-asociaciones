# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Definir rutas relativas desde deployment/mac_exe/
FRONTEND_DIR = os.path.abspath('../../frontend')

datas = [
    # Archivos estáticos (deben haber sido recolectados previamente con collectstatic)
    (os.path.join(FRONTEND_DIR, 'staticfiles'), 'staticfiles'),
]

# Añadir plantillas de cada aplicación
apps = ['core', 'users', 'socias', 'finanzas', 'eventos', 'proyectos', 'entidades']
for app in apps:
    template_path = os.path.join(FRONTEND_DIR, app, 'templates')
    if os.path.exists(template_path):
        datas.append((template_path, os.path.join(app, 'templates')))

# Importaciones ocultas necesarias para Uvicorn y Django
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'whitenoise.middleware',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.core.mail.backends.smtp',
    'django.core.mail.backends.console',
    'django.db.backends.sqlite3',
]

# Recolectar automáticamente todos los submódulos de nuestras apps
# Esto asegura que se incluyan migrations, templatetags, context_processors, utils, etc.
project_apps = ['asonet_django', 'core', 'users', 'socias', 'finanzas', 'eventos', 'proyectos', 'entidades']
for app in project_apps:
    try:
        hiddenimports.extend(collect_submodules(app))
    except Exception as e:
        print(f"Advertencia: No se pudieron recolectar submódulos de {app}: {e}")

a = Analysis(
    ['run_app.py'],
    pathex=[FRONTEND_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestorAsociaciones',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # True para ver logs en terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
