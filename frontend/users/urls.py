"""
URLs para el módulo users
Organizadas por categorías de funcionalidad
"""
from django.urls import path, include
from . import views
from .views_auth import user_login, user_logout, home
from .views_dashboard import dashboard, drive_config, drive_files, drive_callback
from .views_users import usuarios_web, crear_usuario_web, editar_usuario_web, eliminar_usuario_web

app_name = "users"

# =============================================================================
# URLs DE AUTENTICACIÓN
# =============================================================================
auth_patterns = [
    path("", home, name="home"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
]

# =============================================================================
# URLs DEL DASHBOARD
# =============================================================================
dashboard_patterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/drive/config/", drive_config, name="drive_config"),
    path("dashboard/drive/callback/", drive_callback, name="drive_callback"),
    path("dashboard/drive/files/", drive_files, name="drive_files"),
]

# =============================================================================
# URLs DE GESTIÓN DE USUARIOS WEB (Solo admins)
# =============================================================================
usuarios_patterns = [
    path("usuarios-web/", usuarios_web, name="usuarios_web"),
    path("usuarios-web/crear/", crear_usuario_web, name="crear_usuario_web"),
    path("usuarios-web/editar/<int:user_id>/", editar_usuario_web, name="editar_usuario_web"),
    path("usuarios-web/eliminar/<int:user_id>/", eliminar_usuario_web, name="eliminar_usuario_web"),
]

# =============================================================================
# PATRÓN PRINCIPAL DE URLs
# =============================================================================
urlpatterns = auth_patterns + dashboard_patterns + usuarios_patterns
