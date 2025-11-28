# Guía de Uso con Docker (Para Desarrolladores)

Esta configuración permite levantar todo el entorno de desarrollo utilizando Docker y Docker Compose.

## Requisitos

- Docker
- Docker Compose

## Instrucciones Rápidas

1.  **Navega a esta carpeta:**
    ```bash
    cd deployment/docker
    ```

2.  **Levanta el entorno:**
    ```bash
    docker-compose up --build
    ```

3.  **Accede a la aplicación:**
    Abre tu navegador en [http://localhost:8000](http://localhost:8000).

## Detalles

- **Volúmenes:** El código fuente (`../../`) se monta dentro del contenedor en `/app`. Esto significa que cualquier cambio que hagas en tu editor de código se reflejará inmediatamente (gracias al auto-reload de Django).
- **Base de Datos:** Se utiliza `db.sqlite3` del directorio raíz. Los datos persistirán entre reinicios del contenedor.
- **Dependencias:** Si añades nuevas librerías a `requirements.txt`, tendrás que reconstruir el contenedor con `docker-compose up --build`.

## Comandos Útiles

- **Crear superusuario (dentro del contenedor):**
    ```bash
    docker-compose exec web python frontend/manage.py createsuperuser
    ```

- **Ejecutar migraciones manuales:**
    ```bash
    docker-compose exec web python frontend/manage.py migrate
    ```

- **Parar el entorno:**
    Pulsa `Ctrl+C` o ejecuta:
    ```bash
    docker-compose down
    ```
