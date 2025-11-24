#!/usr/bin/env python
"""
Script para crear asociaciones de ejemplo
Solo debe ser ejecutado p    # Asociar el usuario a una asociación existente (elige la creada 'AV004' si está disponible)
    try:
        user_obj = User.objects.get(username=test_username)
        asociacion_obj = AsociacionVecinal.objects.filter(numero_registro='AV004').first()
        if asociacion_obj:
            # Intentar usar el perfil; si no existe, crearlo
            if hasattr(user_obj, 'profile'):
                user_obj.profile.asociacion = asociacion_obj
                user_obj.profile.save()
            else:
                # Crear perfil manualmente para asegurar la relación
                from users.models import UserProfile
                UserProfile.objects.create(user=user_obj, asociacion=asociacion_obj)
            print(f"✅ Usuario '{test_username}' asociado a la asociación: {asociacion_obj.nombre}")
        else:
            print("⚠️  No se encontró la asociación 'AV004' para asociar al usuario")
"""
import os
import django
import argparse
import subprocess
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
django.setup()

from core.models import AsociacionVecinal
from django.contrib.auth import get_user_model

def create_sample_associations():
    """Crear asociaciones de ejemplo"""

    associations = [
        {
            'nombre': 'Asociación Vecinal Centro',
            'telefono': '+34 91 123 4567',
            'direccion': 'Calle Mayor, 15',
            'distrito': 'Centro',
            'numero_registro': 'AV001',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28013'
        },
        {
            'nombre': 'Asociación Vecinal Salamanca',
            'telefono': '+34 91 234 5678',
            'direccion': 'Calle Serrano, 45',
            'distrito': 'Salamanca',
            'numero_registro': 'AV002',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28006'
        },
        {
            'nombre': 'Asociación Vecinal Chamberí',
            'telefono': '+34 91 345 6789',
            'direccion': 'Calle Fuencarral, 87',
            'distrito': 'Chamberí',
            'numero_registro': 'AV003',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28010'
        },
        {
            'nombre': 'Asociación Vecinal Lucero',
            'telefono': '+34 91 456 7890',
            'direccion': 'Calle de Lucero, 10',
            'distrito': 'Lucero',
            'numero_registro': 'AV004',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28019'
        }
    ]

    created_count = 0
    for assoc_data in associations:
        # Verificar si ya existe
        if not AsociacionVecinal.objects.filter(numero_registro=assoc_data['numero_registro']).exists():
            # Filtrar sólo los campos que realmente existen en el modelo
            allowed_fields = {
                f.name for f in AsociacionVecinal._meta.get_fields()
                if getattr(f, 'concrete', False) and not getattr(f, 'auto_created', False)
            }
            model_kwargs = {k: v for k, v in assoc_data.items() if k in allowed_fields}
            AsociacionVecinal.objects.create(**model_kwargs)
            created_count += 1
            print(f"✅ Creada: {assoc_data['nombre']}")
        else:
            print(f"⚠️  Ya existe: {assoc_data['nombre']}")

    print(f"\n🎉 Proceso completado: {created_count} asociaciones creadas")
    print(f"📊 Total de asociaciones: {AsociacionVecinal.objects.count()}")

    # Crear usuario de prueba
    User = get_user_model()
    test_username = 'user'
    test_password = 'user'
    if not User.objects.filter(username=test_username).exists():
        user = User.objects.create_user(username=test_username, password=test_password)
        # NO establecer is_staff=True para que NO tenga acceso al admin de Django
        user.save()
        print(f"✅ Usuario de prueba creado: {test_username} / {test_password}")
    else:
        print(f"⚠️  Usuario de prueba ya existe: {test_username}")

    # Asociar el usuario a una asociación existente (elige la creada 'AV004' si está disponible)
    try:
        user_obj = User.objects.get(username=test_username)
        # Asegurar que NO es staff (no acceso al admin de Django)
        if user_obj.is_staff:
            user_obj.is_staff = False
            user_obj.save()
            print(f"✅ Removidos permisos de staff de usuario '{test_username}'")

        asociacion_obj = AsociacionVecinal.objects.filter(numero_registro='AV004').first()
        if asociacion_obj:
            # Intentar usar el perfil; si no existe, crearlo
            if hasattr(user_obj, 'profile'):
                user_obj.profile.asociacion = asociacion_obj
                user_obj.profile.role = 'admin'  # Admin de la asociación (no de Django)
                user_obj.profile.save()
            else:
                # Crear perfil manualmente para asegurar la relación
                from users.models import UserProfile
                UserProfile.objects.create(user=user_obj, asociacion=asociacion_obj, role='admin')
            print(f"✅ Usuario '{test_username}' asociado a la asociación: {asociacion_obj.nombre}")
            print(f"✅ Usuario '{test_username}' configurado como admin de asociación (NO admin de Django)")
        else:
            print("⚠️  No se encontró la asociación 'AV004' para asociar al usuario")
    except Exception as e:
        print(f"❌ Error al asociar usuario a asociación: {e}")

if __name__ == '__main__':
    # Mantener compatibilidad: si se ejecuta sin args se crean asociaciones y usuario
    parser = argparse.ArgumentParser(description='Crear datos de ejemplo y/o importar raw_data')
    parser.add_argument('--import-socias', action='store_true', help='Lanzar importación de socias desde .raw_data')
    parser.add_argument('--asociacion-id', type=int, default=1, help='ID de la asociación destino para la importación de socias')
    parser.add_argument('--asociacion-registro', type=str, help="Número de registro de la asociación destino (ej. 'AV004' para Lucero)")
    parser.add_argument('--dry-run', action='store_true', help='Pasar --dry-run al importador de socias')

    args = parser.parse_args()

    # Acción principal: crear asociaciones y usuario
    create_sample_associations()

    # Si se solicita, ejecutar el importador existente
    if args.import_socias:
        importer_script = '.migrations/import_socias_from_excel.py'

        # Determinar ID de la asociación destino
        target_id = args.asociacion_id

        # Si se pasa --asociacion-registro, resolver su id
        if args.asociacion_registro:
            assoc = AsociacionVecinal.objects.filter(numero_registro=args.asociacion_registro).first()
            if assoc:
                target_id = assoc.id
            else:
                print(f"Advertencia: no se encontró asociación con numero_registro={args.asociacion_registro}; usando asociacion_id={target_id}")
        else:
            # Si no se pasó registro y el valor por defecto es 1, preferir la asociación Lucero (AV004) si existe
            if args.asociacion_id == 1:
                lucero = AsociacionVecinal.objects.filter(numero_registro='AV004').first()
                if lucero:
                    target_id = lucero.id
                    print(f"Usando la asociación 'Asociación Vecinal Lucero' (numero_registro='AV004') como destino (id={target_id})")

        cmd = [sys.executable, importer_script, '--asociacion_id', str(target_id)]
        if args.dry_run:
            cmd.append('--dry-run')

        print(f"\nEjecutando importador de socias: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            print("\nImportador finalizó correctamente")
        except subprocess.CalledProcessError as e:
            print(f"\nEl importador devolvió un código de error: {e.returncode}")