#!/usr/bin/env python
"""
Script para analizar el archivo de socias y planificar la importación
"""
import os
import sys
import pandas as pd
from pathlib import Path

def analyze_socias_file():
    """Analizar el archivo de socias ODS"""

    # Ruta al archivo (relativa al directorio del script)
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    file_path = project_dir / '.raw_data' / 'socias' / 'LISTA SOCIOS diciembre-2024.ods'

    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return None

    print(f"📁 Analizando archivo: {file_path.name}")
    print(f"📏 Tamaño del archivo: {file_path.stat().st_size / 1024:.1f} KB\n")

    try:
        # Leer el archivo ODS
        print("📊 Leyendo archivo ODS...")
        df = pd.read_excel(file_path, engine='odf')

        print(f"✅ Archivo leído correctamente")
        print(f"📋 Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas\n")

        # Mostrar información de las columnas
        print("📌 Columnas encontradas:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")

        print("\n📝 Primeras 5 filas de datos:")
        print("=" * 80)

        # Mostrar las primeras filas
        for idx, row in df.head().iterrows():
            print(f"\nFila {idx + 1}:")
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    value = "(vacío)"
                print(f"  {col}: {value}")

        print("\n" + "=" * 80)

        # Estadísticas básicas
        print("\n📊 Estadísticas:")
        print(f"  - Total de registros: {len(df)}")
        print(f"  - Registros con datos completos: {len(df.dropna(how='all'))}")

        # Analizar columnas que podrían estar vacías
        print("\n🔍 Análisis de completitud por columna:")
        for col in df.columns:
            non_null = df[col].count()
            percentage = (non_null / len(df)) * 100
            print(f"  {col}: {non_null}/{len(df)} ({percentage:.1f}% completo)")

        # Detectar posibles duplicados
        if 'nombre' in df.columns and 'apellidos' in df.columns:
            df['nombre_completo'] = df['nombre'].astype(str) + ' ' + df['apellidos'].astype(str)
            duplicados = df['nombre_completo'].duplicated().sum()
            print(f"\n⚠️  Posibles duplicados por nombre: {duplicados}")

        return df

    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return None

def create_import_plan(df):
    """Crear plan de importación basado en el análisis"""

    if df is None:
        return

    print("\n" + "="*60)
    print("📋 PLAN DE IMPORTACIÓN")
    print("="*60)

    # Mapeo de columnas
    print("\n1️⃣ MAPEO DE COLUMNAS:")
    print("   Mapear columnas del Excel a campos del modelo Socia:")

    # Campos del modelo Socia
    model_fields = [
        'numero_socia', 'nombre', 'apellidos', 'telefono', 'direccion',
        'provincia', 'codigo_postal', 'pais', 'nacimiento', 'pagado', 'descripcion'
    ]

    print(f"\n   📝 Campos disponibles en el modelo Socia:")
    for field in model_fields:
        print(f"      - {field}")

    print(f"\n   📊 Columnas en el archivo Excel:")
    for i, col in enumerate(df.columns, 1):
        print(f"      {i:2d}. {col}")

    print("\n2️⃣ PASOS DE IMPORTACIÓN:")
    print("   1. Limpiar y validar datos del Excel")
    print("   2. Crear/obtener asociación de destino")
    print("   3. Mapear columnas Excel → campos del modelo")
    print("   4. Generar números de socia automáticamente")
    print("   5. Validar datos antes de guardar")
    print("   6. Crear registros en la base de datos")
    print("   7. Generar reporte de importación")

    print("\n3️⃣ CONSIDERACIONES:")
    print("   ⚠️  Números de socia: Se asignarán automáticamente")
    print("   ⚠️  Asociación: Debe especificarse la asociación de destino")
    print("   ⚠️  Duplicados: Verificar antes de importar")
    print("   ⚠️  Validación: Campos requeridos deben estar presentes")

    print("\n4️⃣ ARCHIVO DE MIGRACIÓN:")
    print("   📁 Ubicación: .migrations/import_socias_from_excel.py")
    print("   🔧 Funcionalidad: Script Django independiente")
    print("   📊 Logging: Reporte detallado del proceso")

if __name__ == "__main__":
    print("🔍 ANÁLISIS DE ARCHIVO DE SOCIAS")
    print("=" * 50)

    df = analyze_socias_file()
    create_import_plan(df)