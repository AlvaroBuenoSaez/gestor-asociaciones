# 📁 Nueva Estructura de Templates - AsoNet

## 🎯 Estructura Reorganizada

La reorganización de templates sigue una arquitectura modular y escalable que separa las responsabilidades por funcionalidad.

```
users/templates/
├── base/                          # 🏗️ Plantillas base y layout
│   ├── base.html                  # Base principal con Bootstrap y mensajes
│   └── base_dashboard.html        # Base del dashboard con navegación
├── auth/                          # 🔐 Autenticación
│   ├── login.html                 # Formulario de login
│   └── no_association.html        # Mensaje sin asociación
├── dashboard/                     # 📊 Dashboard principal
│   └── dashboard.html             # Vista principal del dashboard
├── usuarios_web/                  # 👥 Gestión de usuarios web
│   ├── list.html                  # Lista de usuarios
│   ├── create.html                # Crear usuario
│   ├── edit.html                  # Editar usuario
│   └── delete.html                # Eliminar usuario
├── socias/                        # 👩‍🤝‍👩 Gestión de socias
│   └── list.html                  # Lista de socias (preparado)
├── contabilidad/                  # 💰 Gestión financiera
│   └── dashboard.html             # Dashboard contable (preparado)
├── actividades/                   # 🎯 Gestión de actividades
│   └── list.html                  # Lista de actividades (preparado)
└── mapas/                         # 🗺️ Mapas interactivos
    └── viewer.html                # Visor de mapas (preparado)
```

## 🔧 Ventajas de la Nueva Estructura

### ✅ **Modularidad**
- Cada sección tiene su propio directorio
- Fácil localización de plantillas
- Separación clara de responsabilidades

### ✅ **Escalabilidad**
- Nuevas funcionalidades se añaden en su propio directorio
- No hay saturación de archivos en un solo lugar
- Fácil mantenimiento a largo plazo

### ✅ **Reutilización**
- `base/base.html`: Base común para todas las páginas
- `base/base_dashboard.html`: Base para páginas del dashboard
- Componentes compartidos centralizados

### ✅ **Claridad en Nomenclatura**
- `list.html`: Listas de elementos
- `create.html`: Formularios de creación
- `edit.html`: Formularios de edición
- `delete.html`: Confirmaciones de eliminación
- `dashboard.html`: Vistas tipo dashboard

## 🏗️ Arquitectura de Templates

### Base Templates

#### `base/base.html`
- HTML5 base con Bootstrap 5
- Sistema de mensajes automático
- Bloques configurables: `title`, `content`, `extra_css`, `extra_js`
- Auto-hide de alertas después de 5 segundos

#### `base/base_dashboard.html`
- Extiende de `base/base.html`
- Navegación completa con menús
- Responsive design
- Control de acceso por roles
- **Bloque principal**: `dashboard_content` (para evitar conflictos con `content`)

### Template Structure Pattern

```html
{% extends 'base/base_dashboard.html' %}

{% block title %}Sección - Dashboard{% endblock %}

{% block dashboard_content %}
<div class="container-fluid">
    <!-- Header with actions -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2>🔸 Título de Sección</h2>
            <p class="text-muted">Descripción</p>
        </div>
        <div class="btn-group">
            <!-- Action buttons -->
        </div>
    </div>

    <!-- Statistics cards -->
    <div class="row mb-4">
        <!-- Stats -->
    </div>

    <!-- Main content -->
    <div class="card">
        <!-- Content -->
    </div>
</div>
{% endblock %}
```

## 🚀 Preparación para Nuevas Secciones

### Para agregar una nueva sección:

1. **Crear directorio**: `templates/nueva_seccion/`
2. **Crear plantillas base**:
   - `list.html` - Lista de elementos
   - `create.html` - Crear elemento
   - `edit.html` - Editar elemento
   - `delete.html` - Confirmar eliminación
3. **Actualizar vistas**: Referenciar nuevas rutas de plantillas
4. **Actualizar navegación**: Añadir al menú en `base_dashboard.html`

### Ejemplo de nueva sección "Eventos":

```bash
mkdir templates/eventos/
# Crear: list.html, create.html, edit.html, delete.html
```

```python
# En views_eventos.py
return render(request, 'eventos/list.html', context)
```

## 📝 Nomenclatura de Archivos

### Estándar establecido:
- **`list.html`**: Listados y tablas
- **`create.html`**: Formularios de creación
- **`edit.html`**: Formularios de edición
- **`delete.html`**: Confirmaciones de eliminación
- **`dashboard.html`**: Vistas tipo dashboard con estadísticas
- **`viewer.html`**: Visualizadores (mapas, gráficos, etc.)

### Para formularios complejos:
- **`form.html`**: Formulario genérico
- **`wizard.html`**: Formularios multi-paso
- **`modal.html`**: Formularios en modal

## 🔄 Migración Completada

### ✅ **Archivos Migrados:**
- ✅ `users/base_dashboard.html` → `base/base_dashboard.html`
- ✅ `users/login.html` → `auth/login.html`
- ✅ `users/no_association.html` → `auth/no_association.html`
- ✅ `users/dashboard.html` → `dashboard/dashboard.html`
- ✅ `users/usuarios_web.html` → `usuarios_web/list.html`
- ✅ `users/crear_usuario_web.html` → `usuarios_web/create.html`
- ✅ `users/editar_usuario_web.html` → `usuarios_web/edit.html`
- ✅ `users/eliminar_usuario_web.html` → `usuarios_web/delete.html`
- ✅ `users/socias.html` → `socias/list.html`
- ✅ `users/contabilidad.html` → `contabilidad/dashboard.html`
- ✅ `users/actividades.html` → `actividades/list.html`
- ✅ `users/mapas.html` → `mapas/viewer.html`

### ✅ **Referencias Actualizadas:**
- ✅ Todas las vistas actualizadas con nuevas rutas
- ✅ Extends corregidos en todas las plantillas
- ✅ Template base mejorado con mejor estructura
- ✅ Sistema de mensajes centralizado

## 🎨 Próximos Pasos

Esta estructura está preparada para:
- 📊 Implementar dashboard de socias
- 💰 Sistema de contabilidad completo
- 🎯 Gestión de actividades y eventos
- 🗺️ Mapas interactivos con geolocalización
- 📱 API REST (templates JSON)
- 🔔 Sistema de notificaciones

La nueva estructura es **100% escalable** y sigue las mejores prácticas de Django para organización de templates.