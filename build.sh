#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🎨 Recopilando archivos estáticos..."
# Aseguramos que estamos en el directorio correcto para encontrar manage.py
# manage.py está en frontend/
python frontend/manage.py collectstatic --no-input

echo "🗄️ Aplicando migraciones..."
python frontend/manage.py migrate
