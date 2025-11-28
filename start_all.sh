#!/bin/bash

echo "🚀 Iniciando Gestor de Asociaciones (Modo Unificado)..."

# Asegurarnos de estar en el directorio correcto
cd "$(dirname "$0")"

# Iniciar Servidor Unificado (Django + FastAPI)
# Ahora usamos el wsgi.py modificado que monta FastAPI en /api
echo "📦 Levantando Servidor Unificado (Puerto 8000)..."
echo "   - Frontend: http://localhost:8000"
echo "   - Backend API: http://localhost:8000/api/docs"

cd frontend
python manage.py runserver 8000
