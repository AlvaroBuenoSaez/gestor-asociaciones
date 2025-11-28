import os
import sys
from pathlib import Path

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
sys.path.append(str(FRONTEND_DIR))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asonet_django.settings")

import django
django.setup()

from django.contrib.auth.models import User

def run():
    username = os.getenv('ADMIN_USER')
    password = os.getenv('ADMIN_PASS')
    email = os.getenv('ADMIN_EMAIL', 'admin@asonet.com')

    if not username or not password:
        print("⚠️ No se han definido ADMIN_USER o ADMIN_PASS en las variables de entorno.")
        print("   Saltando creación automática de superusuario.")
        return

    if not User.objects.filter(username=username).exists():
        print(f"👤 Creando superusuario '{username}'...")
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print("✅ Superusuario creado correctamente.")
        except Exception as e:
            print(f"❌ Error al crear superusuario: {e}")
    else:
        print(f"ℹ️ El superusuario '{username}' ya existe.")

if __name__ == "__main__":
    run()
