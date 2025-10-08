#!/u"""

import os
import sys
import django

# Configurar Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
django.setup()

from core.models import AsociacionVecinal
from proyectos.models import Proyecto
from eventos.models import Evento
from finanzas.models import Transaccion
from socias.models import Socia

"""
Script de verificación de datos importados de AVL Lucero
Muestra un resumen de los datos importados para verificar la correcta carga
"""

def verificar_datos():
    """Verificar y mostrar los datos importados"""
    print("🔍 VERIFICACIÓN DE DATOS IMPORTADOS")
    print("="*60)

    # Obtener la asociación
    try:
        asociacion = AsociacionVecinal.objects.get(id=1)
        print(f"📍 Asociación: {asociacion.nombre}")
    except AsociacionVecinal.DoesNotExist:
        print("❌ No se encontró la asociación con ID 1")
        return

    print(f"📧 Email: {asociacion.email}")
    print(f"📍 Dirección: {asociacion.direccion}")
    print(f"📞 Teléfono: {asociacion.telefono}")
    print()

    # Verificar socias
    socias_count = Socia.objects.filter(asociacion=asociacion).count()
    print(f"👥 SOCIAS: {socias_count} registradas")
    if socias_count > 0:
        socias_pagadas = Socia.objects.filter(asociacion=asociacion, pagado=True).count()
        socias_pendientes = socias_count - socias_pagadas
        print(f"   ✅ Al día: {socias_pagadas}")
        print(f"   ⚠️  Pendientes: {socias_pendientes}")

        # Mostrar algunas socias de ejemplo
        primeras_socias = Socia.objects.filter(asociacion=asociacion).order_by('numero_socia')[:3]
        print("   📋 Primeras socias:")
        for socia in primeras_socias:
            estado = "✅" if socia.pagado else "⚠️"
            print(f"      {estado} #{socia.numero_socia}: {socia.nombre} {socia.apellidos}")
    print()

    # Verificar proyectos
    proyectos = Proyecto.objects.filter(asociacion=asociacion)
    print(f"🏗️  PROYECTOS: {proyectos.count()} activos")
    for proyecto in proyectos:
        estado_icon = {"pendiente": "⏳", "en_curso": "🔄", "finalizado": "✅"}.get(proyecto.estado, "❓")
        print(f"   {estado_icon} {proyecto.nombre}")
        print(f"      👤 Responsable: {proyecto.responsable}")
        print(f"      📅 Inicio: {proyecto.fecha_inicio}")
        if proyecto.fecha_final:
            print(f"      🏁 Fin previsto: {proyecto.fecha_final}")
        print(f"      📍 Lugar: {proyecto.lugar}")
        print()

    # Verificar eventos
    eventos = Evento.objects.filter(asociacion=asociacion).order_by('fecha')
    print(f"🎪 EVENTOS: {eventos.count()} programados")
    for evento in eventos:
        # Determinar si es pasado, presente o futuro
        from django.utils import timezone
        ahora = timezone.now()
        if evento.fecha < ahora:
            tiempo_icon = "📅"  # Pasado
        else:
            tiempo_icon = "🔜"  # Futuro

        print(f"   {tiempo_icon} {evento.nombre}")
        print(f"      📅 Fecha: {evento.fecha.strftime('%d/%m/%Y %H:%M')}")
        print(f"      📍 Lugar: {evento.lugar}")
        if evento.duracion:
            # Formatear duración
            dias = evento.duracion.days
            horas, resto = divmod(evento.duracion.seconds, 3600)
            minutos = resto // 60
            duracion_str = []
            if dias > 0:
                duracion_str.append(f"{dias} días")
            if horas > 0:
                duracion_str.append(f"{horas}h")
            if minutos > 0:
                duracion_str.append(f"{minutos}min")
            print(f"      ⏱️  Duración: {', '.join(duracion_str)}")
        print()

    # Verificar transacciones
    transacciones = Transaccion.objects.filter(asociacion=asociacion).order_by('-fecha_transaccion')
    print(f"💰 TRANSACCIONES: {transacciones.count()} registradas")

    # Calcular totales
    ingresos = sum(t.cantidad for t in transacciones if t.cantidad > 0)
    gastos = sum(abs(t.cantidad) for t in transacciones if t.cantidad < 0)
    saldo = ingresos - gastos

    print(f"   📈 Ingresos totales: {ingresos:.2f}€")
    print(f"   📉 Gastos totales: {gastos:.2f}€")
    print(f"   💰 Saldo actual: {saldo:.2f}€")
    print()

    # Mostrar últimas transacciones
    print("   💳 Últimas transacciones:")
    for transaccion in transacciones[:5]:
        tipo_icon = "📈" if transaccion.cantidad > 0 else "📉"
        print(f"      {tipo_icon} {transaccion.concepto}: {transaccion.cantidad:.2f}€")
        print(f"         📅 {transaccion.fecha_transaccion}")

    print("\n" + "="*60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("🌐 Servidor disponible en: http://127.0.0.1:8001/")
    print("👤 Login de prueba: admin / admin123")

if __name__ == '__main__':
    verificar_datos()