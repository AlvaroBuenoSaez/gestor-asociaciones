# Despliegue como Ejecutable de Windows (.exe)

Esta carpeta contiene los archivos necesarios para empaquetar la aplicación Django/FastAPI como un ejecutable independiente para Windows utilizando PyInstaller.

## Archivos

*   `run_app.py`: Script de entrada que inicia el servidor Uvicorn y abre el navegador.
*   `gestor.spec`: Archivo de especificación de PyInstaller que define cómo empaquetar la aplicación (incluyendo plantillas y estáticos).

## Requisitos Previos

1.  Python 3.10+ instalado en Windows.
2.  Entorno virtual activado.
3.  Dependencias instaladas (`pip install -r requirements.txt`).
4.  `pyinstaller` instalado (`pip install pyinstaller`).

## Instrucciones de Construcción (Manual)

Desde la raíz del proyecto:

1.  **Recolectar archivos estáticos:**
    Es crucial ejecutar esto antes de construir, ya que el ejecutable incluirá la carpeta `staticfiles`.

    ```bash
    cd frontend
    python manage.py collectstatic --noinput
    cd ..
    ```

2.  **Ejecutar PyInstaller:**
    Navega a esta carpeta y ejecuta el comando de construcción.

    ```bash
    cd deployment/win_exe
    pyinstaller gestor.spec
    ```

3.  **Resultado:**
    El ejecutable se generará en `deployment/win_exe/dist/GestorAsociaciones.exe`.

## Notas sobre la Base de Datos

El ejecutable está configurado para buscar (o crear) el archivo `db.sqlite3` en la **misma carpeta donde reside el .exe**. Esto asegura que los datos persistan entre ejecuciones.

Si distribuyes el `.exe`, asegúrate de que el usuario tenga permisos de escritura en la carpeta donde lo coloque.
