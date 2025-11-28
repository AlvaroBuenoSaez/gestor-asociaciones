# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Definir rutas relativas desde deployment/win_exe/
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
    # Añadir configuración del proyecto
    'asonet_django',
    'asonet_django.settings',
    'asonet_django.urls',
    'asonet_django.asgi',
    # Añadir apps propias a hiddenimports por si acaso
    'core', 'users', 'socias', 'finanzas', 'eventos', 'proyectos', 'entidades',
    'core.apps', 'users.apps', 'socias.apps', 'finanzas.apps', 'eventos.apps', 'proyectos.apps', 'entidades.apps',
]

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
    console=True, # True para ver logs, False para modo ventana silencioso
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
