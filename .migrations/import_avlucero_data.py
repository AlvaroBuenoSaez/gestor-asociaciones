#!/usr/bin/env python
"""
Script de importación de datos reales de la Asociación Vecinal Lucero
Basado en el análisis de https://avlucero.org/

Importa:
- Proyectos activos de la asociación
- Eventos y actividades programadas
- Datos realistas para testing del sistema

Uso:
    python .migrations/import_avlucero_data.py --asociacion_id=1 [--dry-run]

Opciones:
    --asociacion_id: ID de la asociación donde importar los datos
    --dry-run: Ejecutar sin guardar cambios (solo mostrar lo que haría)
    --help: Mostrar esta ayuda
"""

import os
import sys
import django
import argparse
from datetime import datetime, date, timedelta
from decimal import Decimal

# Configurar Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from core.models import AsociacionVecinal
from proyectos.models import Proyecto
from eventos.models import Evento
from finanzas.models import Transaccion

class AVLuceroDataImporter:
    """Importador de datos reales de la Asociación Vecinal Lucero"""

    def __init__(self, asociacion_id, dry_run=False):
        self.asociacion_id = asociacion_id
        self.dry_run = dry_run
        self.asociacion = None
        self.stats = {
            'proyectos_created': 0,
            'eventos_created': 0,
            'transacciones_created': 0,
            'errors': []
        }

    def load_asociacion(self):
        """Cargar la asociación destino"""
        try:
            self.asociacion = AsociacionVecinal.objects.get(id=self.asociacion_id)
            print(f"✅ Asociación encontrada: {self.asociacion.nombre}")
            return True
        except AsociacionVecinal.DoesNotExist:
            print(f"❌ Error: No existe asociación con ID {self.asociacion_id}")
            return False

    def get_proyectos_data(self):
        """Definir los proyectos a importar"""
        return [
            {
                'nombre': 'Plaza Cívica Lucero',
                'responsable': 'Asociación Vecinal Lucero',
                'involucrados': 'Vecindario, Junta Municipal Latina, Ayuntamiento de Madrid',
                'descripcion': 'Iniciativa para la reutilización y acondicionamiento del espacio del antiguo campo de fútbol "Racing Garvín" como plaza cívica para el barrio. Proyecto de recuperación de espacios públicos para uso comunitario.',
                'materiales': 'Mobiliario urbano, pavimentación, zonas verdes, iluminación, juegos infantiles',
                'lugar': 'Antiguo campo de fútbol Racing Garvín, Barrio Lucero',
                'fecha_inicio': date(2024, 3, 1),
                'fecha_final': date(2025, 12, 31),
                'recursivo': False
            },
            {
                'nombre': 'Parque de la Cuña Verde',
                'responsable': 'Movimiento Vecinal Lucero',
                'involucrados': 'AVL, Ecologistas en Acción, Plataforma Ciudadana Cuña Verde',
                'descripcion': 'Mantenimiento y mejora del parque histórico de la Cuña Verde, espacio conseguido gracias al movimiento vecinal. Conservación de zona verde urbana de gran valor ecológico y social.',
                'materiales': 'Plantas autóctonas, sistema de riego, senderos, señalización interpretativa',
                'lugar': 'Cuña Verde del barrio Lucero, entre calles principales',
                'fecha_inicio': date(2023, 1, 15),
                'fecha_final': date(2026, 6, 30),
                'recursivo': True
            },
            {
                'nombre': 'Seguimiento Soterramiento A-5',
                'responsable': 'Comisión de Movilidad AVL',
                'involucrados': 'AVL, FRAVM, Plataforma Anti-A5, vecindario afectado',
                'descripcion': 'Seguimiento activo de las obras de soterramiento de la A-5 a su paso por el barrio. Control de afecciones, reivindicación de mejoras y coordinación de servicios alternativos.',
                'materiales': 'Material de comunicación, estudios técnicos, mediciones acústicas',
                'lugar': 'Autovía A-5 tramo Lucero-Campamento',
                'fecha_inicio': date(2024, 11, 1),
                'fecha_final': date(2027, 3, 31),
                'recursivo': False
            },
            {
                'nombre': 'Recopilación Demandas Vecinales',
                'responsable': 'Secretaría General AVL',
                'involucrados': 'Toda la vecindad del barrio, grupos de trabajo temáticos',
                'descripcion': 'Proceso participativo de recopilación, sistematización y canalización de denuncias y propuestas de mejora del barrio presentadas por la vecindad.',
                'materiales': 'Encuestas, material de difusión, plataforma online, informes',
                'lugar': 'Todo el barrio Lucero',
                'fecha_inicio': date(2024, 1, 10),
                'fecha_final': date(2025, 6, 30),
                'recursivo': True
            },
            {
                'nombre': 'Programa Demandas AVLucero',
                'responsable': 'Junta Directiva AVL',
                'involucrados': 'Comisiones de trabajo, grupos vecinales, representantes políticos',
                'descripcion': 'Elaboración y presentación del documento marco con las demandas específicas más importantes de la asociación ante las administraciones competentes.',
                'materiales': 'Estudios técnicos, propuestas legislativas, material de difusión',
                'lugar': 'Sede AVL y organismos oficiales',
                'fecha_inicio': date(2024, 2, 1),
                'fecha_final': date(2025, 11, 30),
                'recursivo': False
            }
        ]

    def get_eventos_data(self):
        """Definir los eventos a importar"""
        # Calcular fechas para el próximo año
        year_2025 = 2025
        year_2026 = 2026

        return [
            {
                'nombre': 'Fiestas del Barrio Lucero 2025',
                'descripcion': 'Celebración anual de las fiestas populares del barrio Lucero. Nueve días de actividades, conciertos, actividades infantiles, gastronomía y convivencia vecinal.',
                'lugar': 'Calles del barrio Lucero, plaza principal, local AVL',
                'fecha': timezone.make_aware(datetime(year_2025, 9, 13, 16, 0)),
                'duracion': timedelta(days=9),
                'colaboradores': 'Junta Municipal Latina, comerciantes locales, grupos musicales, voluntariado',
                'observaciones': 'Evento principal del año. Requiere múltiples permisos y coordinación con servicios municipales. Participación estimada: 2500 personas.'
            },
            {
                'nombre': 'Carnaval Lucero 2026',
                'descripcion': 'Celebración anual del carnaval del barrio con actividades familiares: pintacaras, batukada, concurso de disfraces, bailes y chocolatada popular.',
                'lugar': 'Metro Lucero y calles adyacentes',
                'fecha': timezone.make_aware(datetime(year_2026, 2, 22, 16, 30)),
                'duracion': timedelta(hours=4),
                'colaboradores': 'Artistas locales, Centro Cultural de la Mujer, voluntariado cultural',
                'observaciones': 'Acceso libre hasta completar aforo. Incluye picoteo vegetariano y vegano. Participación estimada: 150 personas.'
            },
            {
                'nombre': 'Talleres Competencias Digitales 2025',
                'descripcion': 'Programa anual de talleres para reducir la brecha digital. Enseñanza de uso de smartphones, internet, correo electrónico, WhatsApp y servicios digitales.',
                'lugar': 'Local Asociación Vecinal Lucero (C/Alhambra 21)',
                'fecha': timezone.make_aware(datetime(year_2025, 4, 1, 11, 0)),
                'duracion': timedelta(days=240),  # abril a diciembre
                'colaboradores': 'Voluntariado especializado, FRAVM, Fundación ESPLAI',
                'observaciones': 'Grupos reducidos de máximo 8 personas. Horario de mañanas 11:00-13:00. Participación estimada: 120 personas.'
            },
            {
                'nombre': 'Charla Derechos Laborales',
                'descripcion': 'Charla-coloquio sobre derechos laborales organizada por el Comité de Jóvenes. Información sobre convenios, contratos, sindicatos y derechos de autónomos.',
                'lugar': 'Local AVL (C/Alhambra 21)',
                'fecha': timezone.make_aware(datetime(year_2025, 4, 26, 12, 0)),
                'duracion': timedelta(hours=2, minutes=30),
                'colaboradores': 'Comité de Jóvenes AVL, representante sindical, abogado laboralista',
                'observaciones': 'Incluye aperitivo. Actividad previa al 1º de Mayo. Participación estimada: 40 personas.'
            },
            {
                'nombre': 'Semana Cultural - Conciertos',
                'descripcion': 'Programa de conciertos del Conservatorio Teresa Berganza durante la semana cultural del distrito. Múltiples actuaciones de música clásica y contemporánea.',
                'lugar': 'Diversas ubicaciones del barrio',
                'fecha': timezone.make_aware(datetime(year_2025, 3, 10, 19, 0)),
                'duracion': timedelta(days=7),
                'colaboradores': 'Conservatorio Teresa Berganza, Junta Municipal Latina',
                'observaciones': 'Programa conjunto con el distrito. Conciertos gratuitos. Participación estimada: 500 personas.'
            },
            {
                'nombre': 'Manifestación 8M Madrid',
                'descripcion': 'Participación en la manifestación del Día Internacional de la Mujer. Concentración y marcha por los derechos de las mujeres y políticas feministas.',
                'lugar': 'Desde Atocha hasta Plaza de España',
                'fecha': timezone.make_aware(datetime(year_2025, 3, 8, 12, 0)),
                'duracion': timedelta(hours=4),
                'colaboradores': 'Movimiento feminista, FRAVM, organizaciones de mujeres',
                'observaciones': 'Participación como bloque de asociaciones vecinales. Participación estimada: 80 personas.'
            }
        ]

    def get_transacciones_data(self):
        """Definir transacciones de ejemplo relacionadas con proyectos/eventos"""
        return [
            {
                'cantidad': Decimal('-15000.00'),
                'concepto': 'Material Plaza Cívica Lucero',
                'descripcion': 'Compra de materiales para acondicionamiento inicial de la plaza cívica',
                'fecha_transaccion': date(2024, 6, 15),
                'entidad': 'Suministros Urbanos Madrid SL'
            },
            {
                'cantidad': Decimal('25000.00'),
                'concepto': 'Subvención Fiestas Barrio 2025',
                'descripcion': 'Subvención municipal para organización de fiestas del barrio Lucero',
                'fecha_transaccion': date(2025, 7, 1),
                'entidad': 'Junta Municipal Distrito Latina'
            },
            {
                'cantidad': Decimal('-3200.00'),
                'concepto': 'Equipamiento Talleres Digitales',
                'descripcion': 'Tablets y material didáctico para talleres de competencias digitales',
                'fecha_transaccion': date(2025, 3, 20),
                'entidad': 'Tecnología Educativa Madrid'
            },
            {
                'cantidad': Decimal('8000.00'),
                'concepto': 'Subvención FRAVM Formación',
                'descripcion': 'Subvención para programa de talleres de competencias digitales',
                'fecha_transaccion': date(2025, 2, 10),
                'entidad': 'FRAVM - Federación Regional'
            },
            {
                'cantidad': Decimal('-2800.00'),
                'concepto': 'Gastos Encuentro Arte',
                'descripcion': 'Catering, material expositivo y difusión IV Encuentro de Arte',
                'fecha_transaccion': date(2025, 4, 1),
                'entidad': 'Varios proveedores'
            }
        ]

    def import_proyectos(self):
        """Importar proyectos"""
        print("📂 Importando proyectos...")

        for proyecto_data in self.get_proyectos_data():
            try:
                # Verificar si ya existe
                existing = Proyecto.objects.filter(
                    nombre=proyecto_data['nombre'],
                    asociacion=self.asociacion
                ).first()

                if existing:
                    print(f"⚠️  Proyecto '{proyecto_data['nombre']}' ya existe, saltando...")
                    continue

                if not self.dry_run:
                    proyecto = Proyecto.objects.create(
                        asociacion=self.asociacion,
                        **proyecto_data
                    )
                    print(f"✅ Proyecto creado: {proyecto.nombre}")
                else:
                    print(f"🔍 [DRY-RUN] Crearía proyecto: {proyecto_data['nombre']}")

                self.stats['proyectos_created'] += 1

            except Exception as e:
                error_msg = f"Error creando proyecto '{proyecto_data['nombre']}': {str(e)}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)

    def import_eventos(self):
        """Importar eventos"""
        print("🎪 Importando eventos...")

        # Obtener la primera socia de la asociación para usar como responsable
        from socias.models import Socia
        primera_socia = Socia.objects.filter(asociacion=self.asociacion).first()
        
        if not primera_socia:
            print("⚠️  No hay socias en la asociación, no se pueden crear eventos (requieren responsable)")
            return

        for evento_data in self.get_eventos_data():
            try:
                # Verificar si ya existe
                existing = Evento.objects.filter(
                    nombre=evento_data['nombre'],
                    asociacion=self.asociacion
                ).first()

                if existing:
                    print(f"⚠️  Evento '{evento_data['nombre']}' ya existe, saltando...")
                    continue

                if not self.dry_run:
                    # Agregar responsable y asociación a los datos
                    evento_data['responsable'] = primera_socia
                    evento = Evento.objects.create(
                        asociacion=self.asociacion,
                        **evento_data
                    )
                    print(f"✅ Evento creado: {evento.nombre}")
                else:
                    print(f"🔍 [DRY-RUN] Crearía evento: {evento_data['nombre']} (responsable: {primera_socia.nombre})")

                self.stats['eventos_created'] += 1

            except Exception as e:
                error_msg = f"Error creando evento '{evento_data['nombre']}': {str(e)}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)

    def import_transacciones(self):
        """Importar transacciones de ejemplo"""
        print("💰 Importando transacciones...")

        for transaccion_data in self.get_transacciones_data():
            try:
                # Verificar si ya existe
                existing = Transaccion.objects.filter(
                    concepto=transaccion_data['concepto'],
                    asociacion=self.asociacion,
                    fecha_transaccion=transaccion_data['fecha_transaccion']
                ).first()

                if existing:
                    print(f"⚠️  Transacción '{transaccion_data['concepto']}' ya existe, saltando...")
                    continue

                if not self.dry_run:
                    transaccion = Transaccion.objects.create(
                        asociacion=self.asociacion,
                        **transaccion_data
                    )
                    print(f"✅ Transacción creada: {transaccion.concepto}")
                else:
                    print(f"🔍 [DRY-RUN] Crearía transacción: {transaccion_data['concepto']}")

                self.stats['transacciones_created'] += 1

            except Exception as e:
                error_msg = f"Error creando transacción '{transaccion_data['concepto']}': {str(e)}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)

    def print_stats(self):
        """Mostrar estadísticas finales"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE IMPORTACIÓN")
        print("="*60)
        print(f"🏗️  Proyectos creados: {self.stats['proyectos_created']}")
        print(f"🎪 Eventos creados: {self.stats['eventos_created']}")
        print(f"💰 Transacciones creadas: {self.stats['transacciones_created']}")
        print(f"❌ Errores: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\n🚨 ERRORES ENCONTRADOS:")
            for error in self.stats['errors']:
                print(f"   • {error}")

        if self.dry_run:
            print("\n🔍 MODO DRY-RUN: No se han guardado cambios")
        else:
            print(f"\n✅ Datos importados exitosamente a: {self.asociacion.nombre if self.asociacion else 'asociación'}")

    def run(self):
        """Ejecutar la importación completa"""
        print("🚀 INICIANDO IMPORTACIÓN DE DATOS AVL LUCERO")
        print("="*60)

        if not self.load_asociacion():
            return False

        try:
            with transaction.atomic():
                if self.dry_run:
                    # En modo dry-run, hacer rollback al final
                    sid = transaction.savepoint()

                self.import_proyectos()
                self.import_eventos()
                self.import_transacciones()

                if self.dry_run:
                    transaction.savepoint_rollback(sid)

            self.print_stats()
            return True

        except Exception as e:
            print(f"💥 Error grave durante la importación: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Importar datos reales de AVL Lucero')
    parser.add_argument('--asociacion_id', type=int, required=True,
                       help='ID de la asociación donde importar')
    parser.add_argument('--dry-run', action='store_true',
                       help='Ejecutar sin guardar cambios')

    args = parser.parse_args()

    importer = AVLuceroDataImporter(args.asociacion_id, args.dry_run)
    success = importer.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()