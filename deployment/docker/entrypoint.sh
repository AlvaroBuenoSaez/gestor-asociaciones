#!/bin/bash
set -e

# 1. Aplicar migraciones
echo "🔵 Applying database migrations..."
python frontend/manage.py migrate --noinput

# 2. Crear superusuario si no existe
echo "🔵 Checking superuser..."
python frontend/manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('ADMIN_USER', 'admin')
password = os.environ.get('ADMIN_PASS', 'admin123456')
email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

try:
    if not User.objects.filter(username=username).exists():
        print(f'   Creating superuser: {username}')
        User.objects.create_superuser(username, email, password)
    else:
        print(f'   Superuser {username} already exists.')
except Exception as e:
    print(f'   Error creating superuser: {e}')
"

# 3. Iniciar el servidor
echo "🟢 Starting Django server..."
exec python frontend/manage.py runserver 0.0.0.0:8000
