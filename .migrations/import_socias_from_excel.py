#!/usr/bin/env python
"""
Script de importación de socias desde archivo Excel/ODS
Importa datos manteniendo el número de socia original del archivo

Uso:
    python .migrations/import_socias_from_excel.py --asociacion_id=1 [--dry-run]

Opciones:
    --asociacion_id: ID de la asociación donde importar las socias
    --dry-run: Ejecutar sin guardar cambios (solo mostrar lo que haría)
    --help: Mostrar esta ayuda
"""

import os
import sys
import django
import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime

# Configurar Django
from pathlib import Path
# Añadir la raíz del proyecto al sys.path para poder importar settings cuando se ejecute desde Make/subprocess
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asonet_django.settings')
django.setup()

from django.db import transaction
from core.models import AsociacionVecinal
from socias.models import Socia

class SociasImporter:
    """Importador de socias desde archivo Excel/ODS"""

    def __init__(self, asociacion_id, dry_run=False):
        self.asociacion_id = asociacion_id
        self.dry_run = dry_run
        self.stats = {
            'total_rows': 0,
            'processed': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        self.errors_log = []

    def load_data(self):
        """Cargar datos del archivo ODS"""
        file_path = Path('.raw_data/socias/LISTA SOCIOS diciembre-2024.ods')

        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        print(f"📁 Cargando datos desde: {file_path}")

        # Leer archivo ODS
        df = pd.read_excel(file_path, engine='odf')

        # Filtrar filas completamente vacías
        df = df.dropna(how='all')

        self.stats['total_rows'] = len(df)
        print(f"📊 Total de filas cargadas: {self.stats['total_rows']}")

        return df

    def clean_phone_number(self, phone):
        """Limpiar número de teléfono"""
        if pd.isna(phone):
            return ""

        # Convertir a string y limpiar
        phone_str = str(phone).strip()

        # Remover decimales si es un float
        if '.' in phone_str and phone_str.replace('.', '').isdigit():
            phone_str = phone_str.split('.')[0]

        # Remover espacios y caracteres no numéricos excepto +
        phone_clean = ''.join(c for c in phone_str if c.isdigit() or c == '+')

        return phone_clean if len(phone_clean) >= 6 else ""

    def determine_phone(self, row):
        """Determinar el mejor teléfono disponible"""
        phones = []

        # Prioridad: Móvil > Teléfono general > Fijo
        if not pd.isna(row.get('Telf. Mov')):
            phones.append(self.clean_phone_number(row['Telf. Mov']))

        if not pd.isna(row.get('TELEFONO ')):
            phones.append(self.clean_phone_number(row['TELEFONO ']))

        if not pd.isna(row.get('Telf. Fijo')):
            phones.append(self.clean_phone_number(row['Telf. Fijo']))

        # Devolver el primer teléfono válido
        for phone in phones:
            if phone and len(phone) >= 6:
                return phone

        return ""

    def determine_payment_status(self, row):
        """Determinar si ha pagado basado en ULT. P (último pago)"""
        ult_pago = row.get('ULT. P')

        if pd.isna(ult_pago):
            return False

        try:
            year_pago = int(float(ult_pago))
            current_year = datetime.now().year

            # Considerar pagado si pagó en el año actual o anterior
            return year_pago >= current_year - 1
        except (ValueError, TypeError):
            return False

    def clean_postal_code(self, cp):
        """Limpiar código postal"""
        if pd.isna(cp):
            return ""

        cp_str = str(cp).strip()

        # Remover decimales si es un float
        if '.' in cp_str and cp_str.replace('.', '').isdigit():
            cp_str = cp_str.split('.')[0]

        # Asegurar que sea de 5 dígitos para España
        if cp_str.isdigit() and len(cp_str) == 5:
            return cp_str

        return ""

    def create_description(self, row):
        """Crear descripción con información adicional"""
        desc_parts = []

        # Información de pago
        if not pd.isna(row.get('ULT. P')):
            desc_parts.append(f"Último pago: {row['ULT. P']}")

        if not pd.isna(row.get('cuota')):
            desc_parts.append(f"Cuota: {row['cuota']}€")

        # Información bancaria
        if not pd.isna(row.get('bco')):
            desc_parts.append(f"Banco: {row['bco']}")

        # Situación laboral
        if not pd.isna(row.get('s. lab')):
            status_map = {
                'P': 'Pensionista',
                'A': 'Activo',
                'M': 'Otros'
            }
            status = status_map.get(str(row['s. lab']).strip(), str(row['s. lab']))
            desc_parts.append(f"Situación: {status}")

        # Email adicional (columna unnamed)
        email_col = row.get('Unnamed: 16')
        if not pd.isna(email_col) and '@' in str(email_col):
            desc_parts.append(f"Email: {email_col}")

        return " | ".join(desc_parts)

    def map_row_to_socia_data(self, row):
        """Mapear fila del Excel a datos de Socia"""

        # Número de socia - MANTENER EL ORIGINAL
        numero_socia = str(int(float(row['Nº. S ']))) if not pd.isna(row['Nº. S ']) else None

        if not numero_socia:
            raise ValueError("Número de socia requerido")

        # Nombre y apellidos (requeridos)
        nombre = str(row['NOMBRE']).strip() if not pd.isna(row['NOMBRE']) else ""
        apellidos = str(row['APELLIDOS']).strip() if not pd.isna(row['APELLIDOS']) else ""

        if not nombre or not apellidos:
            raise ValueError("Nombre y apellidos son requeridos")

        # Dirección
        direccion = str(row['DIRECCIÓN']).strip() if not pd.isna(row['DIRECCIÓN']) else ""

        # Código postal
        codigo_postal = self.clean_postal_code(row.get('C. P. '))

        # Ciudad/Provincia
        ciudad = str(row['CIUDAD']).strip() if not pd.isna(row['CIUDAD']) else ""
        provincia = ciudad if ciudad else "Madrid"  # Default Madrid si no hay ciudad

        # Teléfono
        telefono = self.determine_phone(row)

        # Estado de pago
        pagado = self.determine_payment_status(row)

        # Descripción con información adicional
        descripcion = self.create_description(row)

        return {
            'numero_socia': numero_socia,
            'nombre': nombre,
            'apellidos': apellidos,
            'telefono': telefono,
            'direccion': direccion,
            'provincia': provincia,
            'codigo_postal': codigo_postal,
            'pais': 'España',
            'pagado': pagado,
            'descripcion': descripcion
        }

    def process_row(self, idx, row, asociacion):
        """Procesar una fila individual"""
        try:
            self.stats['processed'] += 1

            # Mapear datos
            socia_data = self.map_row_to_socia_data(row)

            # Verificar si ya existe
            existing = Socia.objects.filter(
                asociacion=asociacion,
                numero_socia=socia_data['numero_socia']
            ).first()

            if existing:
                # Actualizar existente
                for field, value in socia_data.items():
                    if field != 'numero_socia':  # No cambiar el número
                        setattr(existing, field, value)

                if not self.dry_run:
                    existing.save()

                self.stats['updated'] += 1
                action = "ACTUALIZADO"
                socia = existing
            else:
                # Crear nuevo
                socia_data['asociacion'] = asociacion

                if not self.dry_run:
                    socia = Socia.objects.create(**socia_data)
                else:
                    socia = Socia(**socia_data)

                self.stats['created'] += 1
                action = "CREADO"

            print(f"✅ Fila {idx+1}: {action} - #{socia_data['numero_socia']} {socia_data['nombre']} {socia_data['apellidos']}")

        except Exception as e:
            self.stats['errors'] += 1
            error_msg = f"Fila {idx+1}: {str(e)}"
            self.errors_log.append(error_msg)
            print(f"❌ {error_msg}")

    def import_socias(self):
        """Ejecutar importación completa"""

        print("🚀 INICIANDO IMPORTACIÓN DE SOCIAS")
        print("=" * 50)

        if self.dry_run:
            print("⚠️  MODO DRY-RUN: No se guardarán cambios")

        # Verificar asociación
        try:
            asociacion = AsociacionVecinal.objects.get(id=self.asociacion_id)
            print(f"🏢 Asociación destino: {asociacion.nombre}")
        except AsociacionVecinal.DoesNotExist:
            print(f"❌ Asociación con ID {self.asociacion_id} no encontrada")
            return False

        # Cargar datos
        try:
            df = self.load_data()
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False

        print("\n📋 Iniciando procesamiento...")
        print("-" * 30)

        # Procesar filas - solo usar transacción si NO es dry-run
        if self.dry_run:
            # En dry-run, procesar sin transacción
            for idx, row in df.iterrows():
                self.process_row(idx, row, asociacion)
        else:
            # En modo real, usar transacción
            with transaction.atomic():
                for idx, row in df.iterrows():
                    self.process_row(idx, row, asociacion)

        # Mostrar resumen
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE IMPORTACIÓN")
        print("=" * 50)
        print(f"📁 Total de filas: {self.stats['total_rows']}")
        print(f"⚙️  Procesadas: {self.stats['processed']}")
        print(f"✅ Creadas: {self.stats['created']}")
        print(f"🔄 Actualizadas: {self.stats['updated']}")
        print(f"⏭️  Omitidas: {self.stats['skipped']}")
        print(f"❌ Errores: {self.stats['errors']}")

        if self.errors_log:
            print(f"\n🚨 ERRORES DETALLADOS:")
            for error in self.errors_log:
                print(f"  - {error}")

        if self.dry_run:
            print(f"\n⚠️  MODO DRY-RUN: Ningún cambio fue guardado")
        else:
            print(f"\n🎉 Importación completada exitosamente!")

        return self.stats['errors'] == 0

def main():
    parser = argparse.ArgumentParser(description='Importar socias desde archivo Excel/ODS')
    parser.add_argument('--asociacion_id', type=int,
                       help='ID de la asociación donde importar')
    parser.add_argument('--asociacion_registro', type=str,
                       help="Número de registro de la asociación destino (ej. 'AV004')")
    parser.add_argument('--dry-run', action='store_true',
                       help='Ejecutar sin guardar cambios (solo mostrar)')

    args = parser.parse_args()

    # Resolver asociacion_registro a ID si fue provisto
    if args.asociacion_registro and not args.asociacion_id:
        assoc = AsociacionVecinal.objects.filter(numero_registro=args.asociacion_registro).first()
        if not assoc:
            print(f"❌ Asociación con numero_registro {args.asociacion_registro} no encontrada")
            sys.exit(1)
        args.asociacion_id = assoc.id

    if not args.asociacion_id:
        print('❌ Debe pasar --asociacion_id o --asociacion_registro')
        sys.exit(1)

    importer = SociasImporter(args.asociacion_id, args.dry_run)
    success = importer.import_socias()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()