# Plan de Refactorización: Separación Backend (FastAPI) y Frontend (Django)

## Estado Actual
- Proyecto Monolítico en Django.
- Base de datos SQLite (`db.sqlite3`).
- Vistas de Django renderizan templates HTML directamente usando el ORM.
- No existe código de FastAPI ni separación de API.

## Objetivo
- **Backend**: FastAPI (API REST, gestión de base de datos). **Arquitectura Hexagonal**.
- **Frontend**: Django (Consumo de API, renderizado de templates).

## Fases del Proyecto

### Fase 1: Configuración del Entorno Backend (Arquitectura Hexagonal)
1.  Crear estructura de carpetas para el backend (`backend/`).
    - Estructura Hexagonal:
        - `domain/`: Entidades y Puertos (Interfaces).
        - `application/`: Casos de Uso y Servicios.
        - `infrastructure/`: Adaptadores (API FastAPI, Repositorios DB).
2.  Inicializar proyecto FastAPI.
3.  Configurar dependencias (`fastapi`, `uvicorn`, `sqlalchemy` o `sqlmodel`, `pydantic`).
4.  Configurar conexión a la base de datos (reutilizando `db.sqlite3` o migrando).

### Fase 2: Migración de Modelos y Datos
1.  Replicar los modelos de Django en Pydantic/SQLModel dentro de FastAPI.
    - Apps a migrar: `users`, `socias`, `eventos`, `finanzas`, `proyectos`.
2.  Asegurar que FastAPI pueda leer/escribir en la misma DB (o planear migración de datos si se cambia de motor).

### Fase 3: Desarrollo de API (Iterativo por Módulo)
Empezaremos por un módulo piloto (ej. `eventos`).
1.  Crear endpoints CRUD en FastAPI:
    - `GET /api/eventos/`
    - `POST /api/eventos/`
    - `GET /api/eventos/{id}`
    - `PUT /api/eventos/{id}`
    - `DELETE /api/eventos/{id}`
2.  Probar endpoints con Swagger UI.

### Fase 4: Adaptación del Frontend (Django)
1.  Crear servicios en Django para consumir la API (usando `httpx` o `requests`).
2.  Refactorizar las Vistas de Django (`views.py`) para que:
    - No usen los Modelos de Django directamente.
    - Llamen a la API de FastAPI para obtener datos.
    - Pasen los datos a los templates.

### Fase 5: Autenticación y Seguridad
1.  Implementar autenticación en FastAPI (JWT).
2.  Gestionar la sesión de usuario en Django y pasar el token a FastAPI.

## Próximos Pasos Inmediatos
1.  Crear carpeta `backend`.
2.  Instalar dependencias.
3.  Crear "Hola Mundo" en FastAPI.
