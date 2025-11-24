# Gestor de Asociaciones — Instrucciones de instalación y ejecución

Este repositorio contiene una API / aplicación Django. El archivo `requirements.txt` ya existe en la raíz: instálalo dentro de un entorno virtual para ejecutar la API.

## Resumen rápido (pasos principales)
- Crear y activar un entorno virtual
- Instalar dependencias con `requirements.txt`
- Aplicar migraciones
- Crear superusuario (opcional)
- Levantar servidor de desarrollo

## Requisitos previos
- Python 3.8+ (recomendado 3.11)
- pip
- git (opcional)
- Node.js y npm (opcional, solo si vas a ejecutar pruebas E2E con Playwright)

## Instrucciones detalladas (Linux / macOS)

1) Clonar el repositorio (si procede)

```bash
git clone https://github.com/AlvaroBuenoSaez/gestor-asociaciones.git
cd gestor-asociaciones
```

2) Crear y activar un entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

3) Instalar dependencias

```bash
pip install -r requirements.txt
```

4) Preparar la base de datos

```bash
python manage.py migrate
```

5) Crear superusuario (opcional)

- El repositorio incluye `superuser.txt` con credenciales de ejemplo. Puedes revisar ese archivo o crear uno nuevo:

```bash
python manage.py createsuperuser
```

6) Cargar datos de ejemplo y migrar `.raw_data` (opcional)

Hay un script de ejemplo `create_sample_associations.py` en la raíz que:

- Crea asociaciones de ejemplo.
- Crea un usuario de prueba `user` (contraseña `user`).
- Opcionalmente puede lanzar el importador que carga socias desde archivos en `.raw_data`.

Ejecutar (vinculado al entorno virtual):

```bash
.venv/bin/python create_sample_associations.py
```

Opciones útiles del script:

- Ejecutar además el importador de socias (usa el importador existente `.migrations/import_socias_from_excel.py`):

```bash
.venv/bin/python create_sample_associations.py --import-socias --asociacion-id 1
```

- Ejecutar el importador en modo "dry-run" (no guarda cambios):

```bash
.venv/bin/python create_sample_associations.py --import-socias --asociacion-id 1 --dry-run
```

Si prefieres ejecutar el importador directamente (script independiente):

```bash
.venv/bin/python .migrations/import_socias_from_excel.py --asociacion_id 1 [--dry-run]
```

Dependencias del importador

El importador usa `pandas` y `odfpy` para leer archivos ODS/Excel. Estas dependencias ya están listadas en `requirements.txt`; instálalas junto con el resto de dependencias:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Ruta de los datos

El importador lee por defecto desde `.raw_data/socias/LISTA SOCIOS diciembre-2024.ods`. Asegúrate de que el fichero existe en esa ruta relativa al repositorio o ajusta la ruta en el script `.migrations/import_socias_from_excel.py`.

Notas de uso

- Ejecuta `python manage.py migrate` antes de importar para asegurar que las tablas existen.
- Revisa el script `create_sample_associations.py` antes de ejecutarlo en entornos compartidos; crea un usuario `user` con contraseña `user` por conveniencia de desarrollo.

7) Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

Exponer en todas las interfaces (útil en contenedores):

```bash
python manage.py runserver 0.0.0.0:8000
```

Cambiar el puerto (ej. 8080):

```bash
python manage.py runserver 8080
```

Accede a la API en http://127.0.0.1:8000/ (o la IP/puerto elegido).

## Comandos útiles

- Ejecutar tests:

```bash
python manage.py test
```

- Crear/actualizar migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

- Si necesitas dependencias de Node (Playwright):

```bash
npm install
npx playwright install
```

## Problemas comunes

- "Couldn't import Django": activa el entorno virtual o instala Django en el entorno activo.
- Permisos de fichero: `db.sqlite3` debe ser escribible por el usuario que ejecuta Django.
- Settings: `manage.py` usa `asonet_django.settings`. Si necesitas otro módulo de configuración, exporta `DJANGO_SETTINGS_MODULE` o usa `--settings`.

## Seguridad y notas finales

- No publiques credenciales reales. `superuser.txt` contiene credenciales de ejemplo: elimínalo antes de subir a un repositorio público.
- Para producción no uses `runserver`. Usa Gunicorn/Daphne/uWSGI y un proxy como Nginx.

---

Si quieres, puedo:
- crear un `requirements-dev.txt` con herramientas de desarrollo,
- limpiar el `requirements.txt` para eliminar paquetes no necesarios en producción,
- añadir un `Dockerfile` y `docker-compose.yml` para desarrollo/despliegue.

Dime cuál de estas opciones prefieres y lo preparo.
