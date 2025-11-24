"""
Vistas para el dashboard principal
"""
from django.shortcuts import render
from django.contrib import messages
from .utils import association_required


@association_required
def dashboard(request):
    """Dashboard principal de la asociación"""
    asociacion = request.user.profile.asociacion
    context = {
        'asociacion': asociacion,
        'user_profile': request.user.profile,
        'section': 'dashboard'
    }
    return render(request, 'dashboard/dashboard.html', context)