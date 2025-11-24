"""
Vistas para gestión de usuarios web (CRUD de usuarios)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .utils import admin_required
from .forms import SimpleUserForm, EditUserForm


@admin_required
def usuarios_web(request):
    """Vista de gestión de usuarios web - solo para admins"""
    asociacion = request.user.profile.asociacion
    usuarios = User.objects.filter(
        profile__asociacion=asociacion,
        is_superuser=False
    ).select_related('profile').order_by('last_name', 'first_name')

    context = {
        'section': 'usuarios_web',
        'usuarios': usuarios,
        'asociacion': asociacion,
    }
    return render(request, 'usuarios_web/list.html', context)


@admin_required
def crear_usuario_web(request):
    """Crear nuevo usuario web"""
    if request.method == 'POST':
        form = SimpleUserForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Crear usuario
                user = form.save()
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.save()

                # Asignar a la asociación del admin
                user.profile.asociacion = request.user.profile.asociacion
                user.profile.role = form.cleaned_data['role']
                user.profile.save()

                messages.success(request, f'Usuario {user.username} creado exitosamente.')
                return redirect('users:usuarios_web')
    else:
        form = SimpleUserForm()

    return render(request, 'usuarios_web/create.html', {'form': form})


@admin_required
def editar_usuario_web(request, user_id):
    """Editar usuario web existente"""
    user_obj = get_object_or_404(User, id=user_id, profile__asociacion=request.user.profile.asociacion)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            # Actualizar rol
            user_obj.profile.role = form.cleaned_data['role']
            user_obj.profile.save()

            messages.success(request, f'Usuario {user_obj.username} actualizado.')
            return redirect('users:usuarios_web')
    else:
        form = EditUserForm(instance=user_obj)

    return render(request, 'usuarios_web/edit.html', {'form': form, 'user_obj': user_obj})


@admin_required
def eliminar_usuario_web(request, user_id):
    """Eliminar usuario web"""
    user_obj = get_object_or_404(User, id=user_id, profile__asociacion=request.user.profile.asociacion)

    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'Usuario {username} eliminado.')
        return redirect('users:usuarios_web')

    return render(request, 'usuarios_web/delete.html', {'user_obj': user_obj})