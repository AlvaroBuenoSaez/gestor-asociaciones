#!/bin/bash

# Función para matar procesos hijos al salir
trap 'kill $(jobs -p)' EXIT

echo "🚀 Iniciando Servidor E2E (Django + FastAPI)..."

# Activar entorno virtual si existe
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

# Instalar dependencias si es necesario (asumiendo que ya están)
# pip install -r ../requirements.txt

# Ejecutar el servidor unificado
# Necesitamos estar en la carpeta e2e para que uvicorn encuentre main:app fácilmente
# o añadir pythonpath. El script main.py ya ajusta el path.

python main.py
