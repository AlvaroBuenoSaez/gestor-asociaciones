#!/usr/bin/env python
"""
Script para crear asociaciones de ejemplo
Solo debe ser ejecutado por superusuarios
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
django.setup()

from users.models import AsociacionVecinal

def create_sample_associations():
    """Crear asociaciones de ejemplo"""

    associations = [
        {
            'nombre': 'Asociación Vecinal Centro',
            'telefono': '+34 91 123 4567',
            'direccion': 'Calle Mayor, 15',
            'distrito': 'Centro',
            'numero_asociacion': 'AV001',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28013'
        },
        {
            'nombre': 'Asociación Vecinal Salamanca',
            'telefono': '+34 91 234 5678',
            'direccion': 'Calle Serrano, 45',
            'distrito': 'Salamanca',
            'numero_asociacion': 'AV002',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28006'
        },
        {
            'nombre': 'Asociación Vecinal Chamberí',
            'telefono': '+34 91 345 6789',
            'direccion': 'Calle Fuencarral, 87',
            'distrito': 'Chamberí',
            'numero_asociacion': 'AV003',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28010'
        },
        {
            'nombre': 'Asociación Vecinal Retiro',
            'telefono': '+34 91 456 7890',
            'direccion': 'Calle Alcalá, 123',
            'distrito': 'Retiro',
            'numero_asociacion': 'AV004',
            'provincia': 'Madrid',
            'pais': 'España',
            'codigo_postal': '28009'
        }
    ]

    created_count = 0
    for assoc_data in associations:
        # Verificar si ya existe
        if not AsociacionVecinal.objects.filter(numero_asociacion=assoc_data['numero_asociacion']).exists():
            AsociacionVecinal.objects.create(**assoc_data)
            created_count += 1
            print(f"✅ Creada: {assoc_data['nombre']}")
        else:
            print(f"⚠️  Ya existe: {assoc_data['nombre']}")

    print(f"\n🎉 Proceso completado: {created_count} asociaciones creadas")
    print(f"📊 Total de asociaciones: {AsociacionVecinal.objects.count()}")

if __name__ == '__main__':
    create_sample_associations()