import pandas as pd
import os
import math
import requests
import time

API_KEY = "ebbcd2121ac241dcbb9339a1843d1727"

def clean_float_to_int_str(val):
    if pd.isna(val):
        return ""
    try:
        return str(int(float(val)))
    except:
        return str(val).strip()

def clean_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def normalize_address_geoapify(direccion, numero, cp, provincia):
    if not direccion:
        return None, None, None

    def call_api(search_text):
        url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            'text': search_text,
            'apiKey': API_KEY,
            'limit': 1,
            'country': 'Spain'
        }
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data['features']:
                    props = data['features'][0]['properties']
                    # Confidence threshold
                    if props.get('rank', {}).get('confidence', 0) > 0.8:
                        return props
        except Exception as e:
            print(f"API Error: {e}")
        return None

    # 1. Try with original data
    search_query = f"{direccion}"
    if numero: search_query += f", {numero}"
    if cp: search_query += f", {cp}"
    if provincia: search_query += f", {provincia}"

    result = call_api(search_query)

    # 2. If not found, try with 28011 Madrid fallback
    if not result:
        if str(cp) != "28011":
            # print(f"  Retrying '{direccion}' in 28011...")
            fallback_query = f"{direccion}"
            if numero: fallback_query += f", {numero}"
            fallback_query += ", 28011 Madrid"
            result = call_api(fallback_query)

    if result:
        new_direccion = result.get('street') or result.get('name') or direccion
        new_cp = result.get('postcode') or cp
        new_provincia = result.get('city') or result.get('state') or provincia
        return new_direccion, new_cp, new_provincia

    return None, None, None

def main():
    input_path = '/home/abueno/workspaces/alvarobueno/avl-propuesta/gestor-asociaciones/.raw_data/socias/LISTA SOCIOS diciembre-2024.ods'
    output_path = '/home/abueno/workspaces/alvarobueno/avl-propuesta/gestor-asociaciones/.raw_data/socias/socias_import_ready.csv'

    # 1. Load existing CSV to cache addresses (avoid re-using Geoapify tokens)
    address_cache = {}
    if os.path.exists(output_path):
        print(f"Loading address cache from {output_path}...")
        try:
            df_cache = pd.read_csv(output_path)
            # Ensure numero_socia is string for matching
            df_cache['numero_socia'] = df_cache['numero_socia'].apply(clean_float_to_int_str)

            for _, row in df_cache.iterrows():
                ns = row['numero_socia']
                if ns:
                    address_cache[ns] = {
                        'direccion': clean_str(row.get('direccion')),
                        'numero': clean_float_to_int_str(row.get('numero')),
                        'piso': clean_str(row.get('piso')),
                        'escalera': clean_str(row.get('escalera')),
                        'codigo_postal': clean_float_to_int_str(row.get('codigo_postal')),
                        'provincia': clean_str(row.get('provincia')),
                        'pais': clean_str(row.get('pais')) or 'España'
                    }
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")

    print(f"Reading from {input_path}...")
    try:
        df = pd.read_excel(input_path, engine='odf')
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Prepare output list
    output_data = []
    total_rows = len(df)
    print(f"Processing {total_rows} rows...")

    for index, row in df.iterrows():
        # Skip empty rows if any
        if pd.isna(row.get('NOMBRE')) and pd.isna(row.get('APELLIDOS')):
            continue

        if index % 10 == 0:
            print(f"Processing row {index}/{total_rows}...")

        # Numero Socia
        numero_socia = clean_float_to_int_str(row.get('Nº. S '))

        # Nombre y Apellidos
        nombre = clean_str(row.get('NOMBRE'))
        apellidos = clean_str(row.get('APELLIDOS'))

        # Telefono (Combine logic)
        telf_raw = clean_float_to_int_str(row.get('TELEFONO '))
        telf_fijo = clean_float_to_int_str(row.get('Telf. Fijo'))
        telf_mov = clean_float_to_int_str(row.get('Telf. Mov'))

        telefonos = [t for t in [telf_raw, telf_mov, telf_fijo] if t]
        telefono = " / ".join(telefonos)

        # Email
        email = clean_str(row.get('e-mail'))

        # Address Logic
        if numero_socia in address_cache:
            # Use cached address
            cached = address_cache[numero_socia]
            direccion = cached['direccion']
            numero = cached['numero']
            piso = cached['piso']
            escalera = cached['escalera']
            codigo_postal = cached['codigo_postal']
            provincia = cached['provincia']
        else:
            # Fallback: Parse but DO NOT use Geoapify
            raw_direccion = clean_str(row.get('DIRECCIÓN'))
            parts = [p.strip() for p in raw_direccion.split(',')]

            direccion = ""
            numero = ""
            piso = ""
            escalera = ""

            if len(parts) > 0:
                direccion = parts[0]
            if len(parts) > 1:
                numero = parts[1]

            for part in parts[2:]:
                part_lower = part.lower()
                if "esc" in part_lower or "escalera" in part_lower:
                    escalera = part
                else:
                    if not piso:
                        piso = part
                    else:
                        piso += f" {part}"

            codigo_postal = clean_float_to_int_str(row.get('C. P. '))
            provincia = clean_str(row.get('CIUDAD'))
            # Skip Geoapify normalization as requested

        # Extra info for description
        extras = []
        # Email is now a proper field, so we don't add it to description

        bco = clean_str(row.get('bco'))
        if bco: extras.append(f"Bco: {bco}")

        s_lab = clean_str(row.get('s. lab'))
        if s_lab: extras.append(f"S. Lab: {s_lab}")

        ult_p = clean_float_to_int_str(row.get('ULT. P'))
        if ult_p: extras.append(f"Ult. P: {ult_p}")

        cuota = clean_float_to_int_str(row.get('cuota'))
        if cuota: extras.append(f"Cuota: {cuota}")

        descripcion = " | ".join(extras)

        # Pagado logic
        pagado = False
        if '2024' in ult_p or '2025' in ult_p:
            pagado = True

        # Create entry
        entry = {
            'numero_socia': numero_socia,
            'nombre': nombre,
            'apellidos': apellidos,
            'telefono': telefono,
            'email': email,
            'direccion': direccion,
            'numero': numero,
            'piso': piso,
            'escalera': escalera,
            'codigo_postal': codigo_postal,
            'provincia': provincia,
            'pais': 'España',
            'nacimiento': '',
            'pagado': pagado,
            'descripcion': descripcion
        }
        output_data.append(entry)

    # Create DataFrame
    out_df = pd.DataFrame(output_data)

    # Save to CSV
    print(f"Saving to {output_path}...")
    out_df.to_csv(output_path, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
