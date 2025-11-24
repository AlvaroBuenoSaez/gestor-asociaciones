"""
Utilidades y decoradores compartidos para las vistas
"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def is_superuser(user):
    """Verifica si el usuario es superusuario"""
    return user.is_superuser


def is_association_admin(user):
    """Verifica si el usuario es administrador de asociación"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_association_admin()


def can_manage_users(user):
    """Verifica si el usuario puede gestionar otros usuarios"""
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.can_manage_users())


def has_association(user):
    """Verifica si el usuario tiene una asociación asignada"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.asociacion


def association_required(view_func):
    """Decorador que requiere que el usuario tenga una asociación asignada"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not has_association(request.user):
            messages.error(request, 'No tienes una asociación asignada. Contacta con el administrador.')
            return redirect('users:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorador que requiere permisos de administrador de asociación"""
    @wraps(view_func)
    @association_required
    @user_passes_test(is_association_admin)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper