"""
Vista temporal para debug de permisos
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.utils import is_association_admin, has_association


@login_required
def debug_permissions(request):
    """Vista para debuggear permisos del usuario"""
    context = {
        'user': request.user,
        'has_profile': hasattr(request.user, 'profile'),
        'has_association': has_association(request.user),
        'is_admin': is_association_admin(request.user),
    }

    if hasattr(request.user, 'profile'):
        context.update({
            'profile': request.user.profile,
            'role': request.user.profile.role,
            'asociacion': request.user.profile.asociacion,
        })

    return render(request, 'debug/permissions.html', context)