import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Configuración
fake = Faker('es_ES')
NUM_SOCIAS = 100
NUM_LUGARES = 15
NUM_PERSONAS = 30
NUM_MATERIALES = 50
NUM_TRANSACCIONES = 200
NUM_ACTIVIDADES = 40
NUM_PROYECTOS = 10

def generate_data():
    print("Generando datos falsos...")

    # --- 1. SOCIAS ---
    socias_data = []
    socias_ids = []
    for i in range(1, NUM_SOCIAS + 1):
        socia_id = str(i)
        socias_ids.append(socia_id)
        socias_data.append({
            'numero_socia': socia_id,
            'nombre': fake.first_name_female(),
            'apellidos': fake.last_name() + ' ' + fake.last_name(),
            'telefono': fake.phone_number(),
            'email': fake.email(),
            'direccion': fake.street_name(),
            'numero': str(random.randint(1, 150)),
            'piso': str(random.randint(1, 10)),
            'escalera': random.choice(['A', 'B', 'C', 'D', 'Izda', 'Dcha']),
            'codigo_postal': fake.postcode(),
            'provincia': fake.city(),
            'pais': 'España',
            'nacimiento': fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            'pagado': random.choice(['Sí', 'No']),
            'descripcion': fake.sentence()
        })
    df_socias = pd.DataFrame(socias_data)

    # --- 2. LUGARES ---
    lugares_data = []
    lugares_nombres = []
    tipos_lugares = ['Centro Cívico', 'Plaza', 'Parque', 'Sala', 'Auditorio', 'Polideportivo', 'Biblioteca']
    for i in range(NUM_LUGARES):
        nombre = f"{random.choice(tipos_lugares)} {fake.city()}"
        if nombre in lugares_nombres:
            nombre = f"{nombre} {i}"
        lugares_nombres.append(nombre)

        lugares_data.append({
            'nombre': nombre,
            'direccion': fake.address(),
            'descripcion': fake.text(max_nb_chars=100),
            'numero': str(random.randint(1, 50)),
            'cp': fake.postcode(),
            'ciudad': fake.city(),
            'pais': 'España'
        })
    df_lugares = pd.DataFrame(lugares_data)

    # --- 3. PROYECTOS (Necesario antes de Personas para vincular) ---
    # Generamos nombres primero para usarlos en Personas, luego creamos el DF completo
    proyectos_nombres = [f"Proyecto {fake.word().capitalize()}" for _ in range(NUM_PROYECTOS)]

    # --- 4. PERSONAS ---
    personas_data = []
    personas_nombres = []
    for _ in range(NUM_PERSONAS):
        nombre = fake.first_name()
        apellidos = fake.last_name()
        personas_nombres.append(f"{nombre} {apellidos}")

        personas_data.append({
            'nombre': nombre,
            'apellidos': apellidos,
            'contacto': fake.job(),
            'cargo': fake.job(),
            'telefono': fake.phone_number(),
            'email': fake.email(),
            'observaciones': fake.sentence(),
            'proyecto_nombre': random.choice(proyectos_nombres) if random.random() > 0.7 else ''
        })
    df_personas = pd.DataFrame(personas_data)

    # --- 5. MATERIALES ---
    materiales_data = []
    tipos_materiales = ['Sillas', 'Mesas', 'Proyector', 'Altavoces', 'Micrófonos', 'Carpas', 'Cartulinas', 'Pinturas', 'Ordenador', 'Impresora']
    for _ in range(NUM_MATERIALES):
        lugar = random.choice(lugares_nombres) if random.random() > 0.2 else ''
        encargado_socia = random.choice(socias_ids) if random.random() > 0.5 else ''
        encargado_persona = random.choice(personas_nombres) if not encargado_socia and random.random() > 0.5 else ''

        materiales_data.append({
            'nombre': f"{random.choice(tipos_materiales)} {fake.word()}",
            'uso': fake.sentence(),
            'precio': round(random.uniform(10.0, 500.0), 2),
            'lugar_nombre': lugar,
            'encargado_persona_nombre': encargado_persona,
            'encargado_socia_numero': encargado_socia
        })
    df_materiales = pd.DataFrame(materiales_data)

    # --- 6. CONTABILIDAD ---
    finanzas_data = []
    for _ in range(NUM_TRANSACCIONES):
        es_ingreso = random.choice([True, False])
        cantidad = round(random.uniform(10.0, 1000.0), 2)
        if not es_ingreso:
            cantidad = -cantidad

        finanzas_data.append({
            'fecha_transaccion': fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
            'cantidad': cantidad,
            'concepto': fake.sentence(nb_words=3),
            'descripcion': fake.sentence(),
            'entidad': fake.company(),
            'fecha_vencimiento': fake.date_between(start_date='today', end_date='+1y').strftime('%Y-%m-%d') if random.random() > 0.8 else ''
        })
    df_finanzas = pd.DataFrame(finanzas_data)

    # --- 7. ACTIVIDADES ---
    eventos_data = []
    for _ in range(NUM_ACTIVIDADES):
        responsable = random.choice(socias_ids)
        lugar = random.choice(lugares_nombres) if random.random() > 0.1 else ''

        eventos_data.append({
            'nombre': f"Actividad {fake.word().capitalize()}",
            'fecha': fake.date_time_between(start_date='-1y', end_date='+1y').strftime('%Y-%m-%d %H:%M:%S'),
            'lugar': lugar,
            'responsable_numero_socia': responsable,
            'responsable_nombre': '', # Opcional, el importador usa el número
            'descripcion': fake.text(),
            'duracion': f"{random.randint(1, 4)}:00:00",
            'colaboradores': fake.company(),
            'observaciones': fake.sentence()
        })
    df_eventos = pd.DataFrame(eventos_data)

    # --- 8. PROYECTOS (Dataframe final) ---
    proyectos_data = []
    for nombre in proyectos_nombres:
        responsable = random.choice(socias_ids) # Usamos ID de socia como responsable string por simplicidad, o nombre
        # El modelo Proyecto tiene responsable como FK a Socia. El exportador pone str(socia).
        # El importador actual de proyectos NO busca por nombre de socia, espera un string o nada.
        # Para que sea útil, pondremos el nombre de una socia aleatoria, aunque el importador actual
        # de proyectos tiene un TODO sobre cómo vincular responsables.

        lugar = random.choice(lugares_nombres) if random.random() > 0.2 else ''
        fecha_inicio = fake.date_between(start_date='-1y', end_date='today')
        fecha_final = fecha_inicio + timedelta(days=random.randint(30, 365))

        proyectos_data.append({
            'nombre': nombre,
            'responsable': f"Socia {responsable}", # Texto descriptivo
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_final': fecha_final.strftime('%Y-%m-%d'),
            'lugar': lugar,
            'descripcion': fake.text(),
            'materiales': fake.sentence(),
            'involucrados': fake.name(),
            'recursivo': random.choice(['Sí', 'No'])
        })
    df_proyectos = pd.DataFrame(proyectos_data)

    # --- GUARDAR A EXCEL ---
    output_file = 'datos_falsos_asociacion.xlsx'
    print(f"Guardando en {output_file}...")

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_socias.to_excel(writer, sheet_name='Socias', index=False)
        df_lugares.to_excel(writer, sheet_name='Lugares', index=False)
        df_personas.to_excel(writer, sheet_name='Personas', index=False)
        df_materiales.to_excel(writer, sheet_name='Materiales', index=False)
        df_finanzas.to_excel(writer, sheet_name='Contabilidad', index=False)
        df_eventos.to_excel(writer, sheet_name='Actividades', index=False)
        df_proyectos.to_excel(writer, sheet_name='Proyectos', index=False)

    print("¡Archivo generado correctamente!")

if __name__ == "__main__":
    generate_data()
