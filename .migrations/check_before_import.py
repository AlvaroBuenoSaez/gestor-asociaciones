#!/usr/bin/env python
"""
Script auxiliar para verificar asociaciones disponibles antes de importar socias
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/abueno/workspaces/alvarobueno/avl-propuesta/gestor-asociaciones')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
django.setup()

from core.models import AsociacionVecinal
from socias.models import Socia

def show_associations():
    """Mostrar asociaciones disponibles"""
    print("🏢 ASOCIACIONES DISPONIBLES")
    print("=" * 40)

    associations = AsociacionVecinal.objects.all()

    if not associations:
        print("❌ No hay asociaciones registradas")
        print("\n💡 Crear una asociación primero:")
        print("   python manage.py shell")
        print("   >>> from core.models import AsociacionVecinal")
        print("   >>> AsociacionVecinal.objects.create(")
        print("   ...     nombre='Mi Asociación',")
        print("   ...     numero_registro='REG001'")
        print("   ... )")
        return False

    for assoc in associations:
        socias_count = Socia.objects.filter(asociacion=assoc).count()
        print(f"ID: {assoc.id:2d} | {assoc.nombre}")
        print(f"        📋 Registro: {assoc.numero_registro}")
        print(f"        👥 Socias actuales: {socias_count}")
        if assoc.descripcion:
            print(f"        📝 {assoc.descripcion}")
        print()

    return True

def show_usage():
    """Mostrar instrucciones de uso"""
    print("\n" + "=" * 60)
    print("🚀 CÓMO USAR EL IMPORTADOR")
    print("=" * 60)
    print()
    print("1️⃣ Primero, ejecutar en modo DRY-RUN para verificar:")
    print("   python .migrations/import_socias_from_excel.py \\")
    print("     --asociacion_id=1 --dry-run")
    print()
    print("2️⃣ Si todo está correcto, ejecutar la importación real:")
    print("   python .migrations/import_socias_from_excel.py \\")
    print("     --asociacion_id=1")
    print()
    print("📌 Opciones disponibles:")
    print("   --asociacion_id: ID de la asociación (requerido)")
    print("   --dry-run: Solo mostrar qué haría sin guardar")
    print("   --help: Mostrar ayuda completa")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Los números de socia del Excel se mantendrán")
    print("   - Se actualizarán socias existentes con el mismo número")
    print("   - Se crearán socias nuevas si no existen")

if __name__ == "__main__":
    print("🔍 PREPARACIÓN PARA IMPORTAR SOCIAS")
    print("=" * 50)

    has_associations = show_associations()

    if has_associations:
        show_usage()

    print("\n✅ Listo para importar!")