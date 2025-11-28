"""
Vistas para gestión de usuarios web (CRUD de usuarios)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .utils import admin_required
from .forms import SimpleUserForm, EditUserForm
from core.api import get_client
import requests

@admin_required
def usuarios_web(request):
    """Vista de gestión de usuarios web - solo para admins"""
    asociacion_id = request.user.profile.asociacion.id
    client = get_client(request)

    try:
        usuarios = client.get("/users/", params={"asociacion_id": asociacion_id})
    except requests.RequestException as e:
        messages.error(request, f"Error al conectar con el backend: {str(e)}")
        usuarios = []

    context = {
        'section': 'usuarios_web',
        'usuarios': usuarios,
        'asociacion': request.user.profile.asociacion,
    }
    return render(request, 'usuarios_web/list.html', context)


@admin_required
def crear_usuario_web(request):
    """Crear nuevo usuario web"""
    if request.method == 'POST':
        form = SimpleUserForm(request.POST)
        if form.is_valid():
            # Extraer datos limpios del formulario
            user_data = {
                "username": form.cleaned_data['username'],
                "email": form.cleaned_data['email'],
                "password": form.cleaned_data['password1'],
                "first_name": form.cleaned_data['first_name'],
                "last_name": form.cleaned_data['last_name'],
                "role": form.cleaned_data['role'],
                "asociacion_id": request.user.profile.asociacion.id
            }

            client = get_client(request)
            try:
                client.post("/users/", data=user_data)
                messages.success(request, f"Usuario {user_data['username']} creado exitosamente.")
                return redirect('users:usuarios_web')
            except requests.RequestException as e:
                detail = getattr(e, 'api_error', {}).get('detail', str(e))
                messages.error(request, f"Error al crear usuario: {detail}")
    else:
        form = SimpleUserForm()

    return render(request, 'usuarios_web/create.html', {'form': form})


@admin_required
def editar_usuario_web(request, user_id):
    """Editar usuario web existente"""
    client = get_client(request)

    # Obtener usuario
    try:
        user_data = client.get(f"/users/{user_id}")

        # Verificar asociación
        if user_data.get('profile', {}).get('asociacion_id') != request.user.profile.asociacion.id:
             messages.error(request, "No tienes permiso para editar este usuario.")
             return redirect('users:usuarios_web')

    except requests.RequestException:
        messages.error(request, "Usuario no encontrado.")
        return redirect('users:usuarios_web')

    # Convertir datos de API a formato inicial de formulario
    initial_data = {
        'username': user_data['username'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'email': user_data['email'],
        'is_active': user_data['is_active'],
        'role': user_data.get('profile', {}).get('role', 'member')
    }

    if request.method == 'POST':
        # Usamos el objeto local para validación de unique constraints en Django form
        user_obj = get_object_or_404(User, id=user_id)
        form = EditUserForm(request.POST, instance=user_obj)

        if form.is_valid():
            update_data = {
                "first_name": form.cleaned_data['first_name'],
                "last_name": form.cleaned_data['last_name'],
                "email": form.cleaned_data['email'],
                "role": form.cleaned_data['role'],
            }

            try:
                client.put(f"/users/{user_id}", data=update_data)
                messages.success(request, f"Usuario {user_data['username']} actualizado.")
                return redirect('users:usuarios_web')
            except requests.RequestException as e:
                detail = getattr(e, 'api_error', {}).get('detail', str(e))
                messages.error(request, f"Error al actualizar: {detail}")
    else:
        user_obj = get_object_or_404(User, id=user_id)
        form = EditUserForm(instance=user_obj)

    return render(request, 'usuarios_web/edit.html', {'form': form, 'user_obj': user_data})


@admin_required
def eliminar_usuario_web(request, user_id):
    """Eliminar usuario web"""
    client = get_client(request)

    try:
        user_data = client.get(f"/users/{user_id}")
    except:
        messages.error(request, "Usuario no encontrado")
        return redirect('users:usuarios_web')

    if request.method == 'POST':
        try:
            client.delete(f"/users/{user_id}")
            messages.success(request, f"Usuario {user_data['username']} eliminado.")
            return redirect('users:usuarios_web')
        except requests.RequestException as e:
             messages.error(request, f"Error al eliminar: {str(e)}")

    return render(request, 'usuarios_web/delete.html', {'user_obj': user_data})