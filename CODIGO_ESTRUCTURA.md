# AsoNet Django - Estructura del Código

## 📁 Organización de Archivos

### Módulos de Vistas (views_*.py)

#### `views_auth.py` - Autenticación
- `user_login()`: Manejo del login con formulario
- `user_logout()`: Cierre de sesión con mensaje
- `home()`: Redirección inteligente según tipo de usuario

#### `views_dashboard.py` - Dashboard y Secciones
- `dashboard()`: Dashboard principal con información de la asociación
- `socias()`: Gestión de socias (próximamente)
- `contabilidad()`: Gestión financiera (próximamente)
- `actividades()`: Gestión de eventos (próximamente)
- `mapas()`: Mapas interactivos (próximamente)

#### `views_users.py` - Gestión de Usuarios Web
- `usuarios_web()`: Lista de usuarios de la asociación
- `crear_usuario_web()`: Crear nuevo usuario
- `editar_usuario_web()`: Editar usuario existente
- `eliminar_usuario_web()`: Eliminar usuario con confirmación

#### `views.py` - Módulo Principal
- Importa y organiza todas las vistas de los módulos especializados
- Mantiene compatibilidad con URLs existentes

### Utilidades (`utils.py`)

#### Funciones de Verificación
- `is_superuser(user)`: Verifica permisos de superusuario
- `is_association_admin(user)`: Verifica permisos de admin de asociación
- `can_manage_users(user)`: Verifica permisos de gestión de usuarios
- `has_association(user)`: Verifica que el usuario tenga asociación

#### Decoradores Personalizados
- `@association_required`: Requiere asociación asignada
- `@admin_required`: Requiere permisos de admin de asociación

### Formularios (`forms.py`)

#### Gestión de Usuarios Web
- `SimpleUserForm`: Crear usuarios (extends UserCreationForm)
- `EditUserForm`: Editar usuarios existentes

#### Gestión de Asociaciones
- `AsociacionForm`: Crear/editar asociaciones
- `UserProfileForm`: Gestionar perfiles de usuario
- `CustomUserCreationForm`: Formulario completo con perfil

#### Formularios para Futuras Secciones
- `SociaForm`: Base para gestión de socias
- `ActividadForm`: Base para gestión de actividades
- `MovimientoContableForm`: Base para movimientos contables

### URLs (`urls.py`)

#### Organización por Categorías
```python
# Autenticación
auth_patterns = [...]

# Dashboard y secciones principales
dashboard_patterns = [...]

# Gestión de usuarios web (solo admins)
usuarios_patterns = [...]
```

## 🔐 Sistema de Permisos

### Niveles de Acceso
1. **Superusuario**: Acceso total al admin de Django
2. **Admin de Asociación**: Dashboard completo + gestión de usuarios
3. **Miembro**: Dashboard limitado (sin gestión de usuarios)

### Protección de Vistas
- `@login_required`: Requiere autenticación
- `@association_required`: Requiere asociación asignada
- `@admin_required`: Requiere permisos de administrador

## 🎨 Plantillas

### Estructura Base
- `base_dashboard.html`: Plantilla base con navegación
- Bootstrap 5 para diseño responsivo
- Iconos Bootstrap Icons

### Secciones Principales
- `dashboard.html`: Dashboard principal
- `usuarios_web.html`: Lista de usuarios con estadísticas
- `crear_usuario_web.html`: Formulario de creación
- `editar_usuario_web.html`: Formulario de edición
- `eliminar_usuario_web.html`: Confirmación de eliminación

### Secciones Futuras (Preparadas)
- `socias.html`: Gestión de socias
- `contabilidad.html`: Gestión financiera
- `actividades.html`: Gestión de eventos
- `mapas.html`: Mapas interactivos

## 🚀 Próximos Pasos

### Funcionalidades Completadas ✅
- [x] Sistema de autenticación
- [x] Dashboard con navegación
- [x] Gestión completa de usuarios web
- [x] Sistema de roles y permisos
- [x] Plantillas responsivas
- [x] Estructura modular escalable

### En Desarrollo 🔄
- [ ] Gestión de socias
- [ ] Sistema de contabilidad
- [ ] Gestión de actividades
- [ ] Mapas interactivos

### Mejoras Futuras 💡
- [ ] API REST para móvil
- [ ] Notificaciones en tiempo real
- [ ] Sistema de chat/mensajería
- [ ] Reportes avanzados
- [ ] Integración con redes sociales

## 🛠️ Comando de Desarrollo

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar servidor
python manage.py runserver

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

## 📋 Notas Técnicas

- **Django**: 5.2.6
- **Base de datos**: SQLite (desarrollo)
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Arquitectura**: Modular con separación de responsabilidades
- **Patrones**: Decoradores personalizados, vistas basadas en funciones
- **Escalabilidad**: Preparado para crecimiento con estructura modular