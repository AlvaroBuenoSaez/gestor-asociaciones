# Plan de Refactorización: Módulo de Usuarios (`users`)

Este documento detalla los pasos para migrar la lógica del módulo `users` de Django al nuevo backend FastAPI con Arquitectura Hexagonal.

## 1. Análisis del Dominio Actual
El módulo `users` gestiona:
- **Autenticación**: Login/Logout (actualmente usando sesiones de Django).
- **Perfil de Usuario**: Extensión del modelo `User` de Django con `UserProfile` (rol, teléfono, asociación, etc.).
- **Gestión de Usuarios**: CRUD de usuarios dentro de una asociación (solo para admins).

## 2. Implementación en Backend (FastAPI)

### A. Capa de Dominio (`backend/app/domain`)
Definir las entidades puras y las interfaces (puertos).
- **Modelos (`models/user.py`)**:
    - `User`: Entidad principal (id, username, email, first_name, last_name).
    - `UserProfile`: Datos extendidos (telefono, direccion, rol, asociacion_id).
    - `UserRole`: Enum (member, admin).
- **Puertos (`ports/user_repository.py`)**:
    - `UserRepository`: Interface con métodos como `get_by_username`, `create`, `update`, `list_by_association`.

### B. Capa de Infraestructura (`backend/app/infrastructure`)
Implementar la persistencia y la API.
- **Persistencia (`persistence/models/user_sql.py`)**:
    - Mapeo SQLAlchemy a las tablas existentes de Django: `auth_user` y `users_userprofile`. **Crucial para mantener compatibilidad de datos.**
- **Repositorio (`persistence/repositories/user_repository_impl.py`)**:
    - Implementación de `UserRepository` usando SQLAlchemy.
- **API (`api/v1/users.py` y `auth.py`)**:
    - `POST /api/v1/auth/login`: Generación de Token (JWT).
    - `GET /api/v1/users/`: Listar usuarios de la asociación.
    - `POST /api/v1/users/`: Crear usuario.
    - `PUT /api/v1/users/{id}`: Actualizar usuario.
    - `DELETE /api/v1/users/{id}`: Eliminar usuario.

### C. Capa de Aplicación (`backend/app/application`)
Casos de uso que orquestan la lógica.
- **Servicios (`services/user_service.py`)**:
    - `UserService`: Lógica de negocio (ej. al crear usuario, asignar asociación del admin, validar permisos).

## 3. Adaptación del Frontend (Django)

Una vez el backend esté funcionando, modificaremos las vistas de Django para que actúen como controladores de frontend.

### Pasos de Migración:
1.  **Login Híbrido**:
    - Mantener el login de Django por ahora para la sesión de navegador.
    - Al hacer login en Django, obtener también un token del Backend (o compartir la base de datos de sesiones temporalmente, aunque JWT es mejor).
    - *Estrategia recomendada*: Que la vista de Django haga una petición al backend para validar credenciales.

2.  **Refactorizar `views_users.py`**:
    - **Listado (`usuarios_web`)**:
        - Reemplazar `User.objects.filter(...)` por `requests.get(API_URL + '/users/', headers=auth_header)`.
        - Pasar los datos JSON recibidos al template.
    - **Creación (`crear_usuario_web`)**:
        - El formulario envía datos a la vista Django.
        - La vista Django valida y envía `requests.post(API_URL + '/users/', json=data)`.
    - **Edición/Eliminación**: Similar proceso.

## 4. Hoja de Ruta de Implementación
1.  [Backend] Configurar conexión DB (SQLAlchemy) a `db.sqlite3`.
2.  [Backend] Crear modelos SQLAlchemy (`auth_user`, `users_userprofile`).
3.  [Backend] Implementar `UserRepository` y `UserService`.
4.  [Backend] Crear endpoints API para listar y crear usuarios.
5.  [Frontend] Modificar `views_users.py` para consumir la API.
