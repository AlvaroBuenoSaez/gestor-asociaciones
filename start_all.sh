#!/bin/bash

# Función para matar procesos hijos al salir
trap 'kill $(jobs -p)' EXIT

echo "🚀 Iniciando Gestor de Asociaciones..."

# Iniciar Backend (FastAPI)
echo "📦 Levantando Backend (Puerto 8000)..."
cd backend
# Activar entorno virtual si existe, o asumir que se corre en el entorno global/activo
# source .venv/bin/activate 2>/dev/null
python run.py &
BACKEND_PID=$!
cd ..

# Esperar un poco para que el backend arranque
sleep 2

# Iniciar Frontend (Django)
echo "🎨 Levantando Frontend (Puerto 8001)..."
cd frontend
# source .venv/bin/activate 2>/dev/null
python manage.py runserver 8001 &
FRONTEND_PID=$!
cd ..

echo "✅ Todo listo!"
echo "   Backend API: http://localhost:8000/docs"
echo "   Frontend Web: http://localhost:8001"
echo "   Presiona Ctrl+C para detener."

# Esperar a que cualquiera de los procesos termine
wait -n
