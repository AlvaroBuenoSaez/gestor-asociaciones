"""
Vistas principales del módulo users
Este archivo importa y organiza las vistas de diferentes módulos especializados
"""

# Importar vistas de autenticación
from .views_auth import (
    user_login,
    user_logout,
    home
)

# Importar vistas del dashboard
from .views_dashboard import (
    dashboard
)

# Importar vistas de gestión de usuarios
from .views_users import (
    usuarios_web,
    crear_usuario_web,
    editar_usuario_web,
    eliminar_usuario_web
)

# Importar utilidades para compatibilidad
from .utils import (
    is_superuser,
    is_association_admin,
    can_manage_users,
    has_association
)