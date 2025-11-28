"""
URLs para el módulo users
Organizadas por categorías de funcionalidad
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views
from .views_auth import (
    user_login, user_logout, home, accept_invite,
    password_reset_request, password_reset_confirm_send, password_reset_done
)
from .views_dashboard import (
    dashboard, drive_callback,
    backend_management, drive_upload, drive_delete, drive_create_folder, drive_select_folder,
    export_socias, import_socias, delete_all_socias,
    export_global_excel, import_global_excel,
    export_finanzas, import_finanzas, delete_all_finanzas,
    export_eventos, import_eventos, delete_all_eventos,
    export_proyectos, import_proyectos, delete_all_proyectos
)
from .views_users import usuarios_web, crear_usuario_web, editar_usuario_web, eliminar_usuario_web

app_name = "users"

# =============================================================================
# URLs DE AUTENTICACIÓN
# =============================================================================
auth_patterns = [
    path("", home, name="home"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("invite/<uuid:token>/", accept_invite, name="accept_invite"),

    # Password Reset Custom Flow
    path("password-reset/", password_reset_request, name="password_reset_request"),
    path("password-reset/confirm-send/", password_reset_confirm_send, name="password_reset_confirm_send"),
    path("password-reset/done/", password_reset_done, name="password_reset_done"),
    
    # Django Built-in views for the actual reset (token verification and new password)
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete')
    ), name="password_reset_confirm"),
    
    path("reset/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name="password_reset_complete"),
]

# =============================================================================
# URLs DEL DASHBOARD
# =============================================================================
dashboard_patterns = [
    path("dashboard/", dashboard, name="dashboard"),

    # Gestión Backend Unificada
    path("dashboard/backend/", backend_management, name="backend_management"),

    # Acciones Drive
    path("dashboard/drive/callback/", drive_callback, name="drive_callback"),
    path("dashboard/drive/upload/", drive_upload, name="drive_upload"),
    path("dashboard/drive/delete/", drive_delete, name="drive_delete"),
    path("dashboard/drive/create-folder/", drive_create_folder, name="drive_create_folder"),
    path("dashboard/drive/select-folder/", drive_select_folder, name="drive_select_folder"),

    # Acciones Datos - Global
    path("dashboard/data/global/export/", export_global_excel, name="export_global_excel"),
    path("dashboard/data/global/import/", import_global_excel, name="import_global_excel"),

    # Acciones Datos - Socias
    path("dashboard/data/socias/export/", export_socias, name="export_socias"),
    path("dashboard/data/socias/import/", import_socias, name="import_socias"),
    path("dashboard/data/socias/delete-all/", delete_all_socias, name="delete_all_socias"),

    # Acciones Datos - Finanzas
    path("dashboard/data/finanzas/export/", export_finanzas, name="export_finanzas"),
    path("dashboard/data/finanzas/import/", import_finanzas, name="import_finanzas"),
    path("dashboard/data/finanzas/delete-all/", delete_all_finanzas, name="delete_all_finanzas"),

    # Acciones Datos - Eventos
    path("dashboard/data/eventos/export/", export_eventos, name="export_eventos"),
    path("dashboard/data/eventos/import/", import_eventos, name="import_eventos"),
    path("dashboard/data/eventos/delete-all/", delete_all_eventos, name="delete_all_eventos"),

    # Acciones Datos - Proyectos
    path("dashboard/data/proyectos/export/", export_proyectos, name="export_proyectos"),
    path("dashboard/data/proyectos/import/", import_proyectos, name="import_proyectos"),
    path("dashboard/data/proyectos/delete-all/", delete_all_proyectos, name="delete_all_proyectos"),
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
