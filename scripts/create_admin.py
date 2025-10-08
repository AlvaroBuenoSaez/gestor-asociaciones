#!/usr/bin/env python
import os
import sys
import django

# Ensure settings module
from pathlib import Path
# Add project root to sys.path so Django settings can be imported when running this script directly
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
pw = 'admin'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=pw, email='admin@example.com')
    print('Superuser created')
else:
    print('Superuser already exists')

# Asociar el superuser a la asociación Lucero (AV004) para poder ver las socias en admin
try:
    admin_user = User.objects.get(username=username)
    from core.models import AsociacionVecinal
    lucero = AsociacionVecinal.objects.filter(numero_registro='AV004').first()
    if lucero:
        # Asegurar que el perfil exista
        if hasattr(admin_user, 'profile'):
            admin_user.profile.asociacion = lucero
            admin_user.profile.save()
        else:
            from users.models import UserProfile
            UserProfile.objects.create(user=admin_user, asociacion=lucero, role='admin')
        print(f"Assigned admin user to association: {lucero.nombre}")
    else:
        print("Asociación 'AV004' no encontrada; no se asoció el superuser")
except Exception as e:
    print(f"Warning: error asignando asociación al superuser: {e}")
