"""
Vistas para gestión de usuarios web (CRUD de usuarios)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .utils import admin_required
from .forms import SimpleUserForm, EditUserForm
import requests

API_URL = "http://localhost:8000/api/v1"

@admin_required
def usuarios_web(request):
    """Vista de gestión de usuarios web - solo para admins"""
    asociacion_id = request.user.profile.asociacion.id

    try:
        response = requests.get(f"{API_URL}/users/", params={"asociacion_id": asociacion_id})
        response.raise_for_status()
        usuarios_data = response.json()

        # Convertir datos JSON a objetos compatibles con el template si es necesario
        # O ajustar el template para usar diccionarios.
        # Por ahora, pasamos la lista de diccionarios.
        # Nota: El template espera objetos User con profile.
        # Para mantener compatibilidad rápida, podemos simular objetos o ajustar el template.
        # Vamos a ajustar el template para que acepte diccionarios o objetos.
        # Pero espera, el template usa user.profile.role.
        # La API devuelve:
        # {
        #   "id": 1,
        #   "username": "...",
        #   "profile": { "role": "...", "asociacion_id": ... }
        # }
        # Esto es compatible con acceso por puntos en Jinja/Django templates si son objetos,
        # pero si son dicts, Django templates permiten user.username igual.

        usuarios = usuarios_data

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

            try:
                response = requests.post(f"{API_URL}/users/", json=user_data)
                response.raise_for_status()
                messages.success(request, f"Usuario {user_data['username']} creado exitosamente.")
                return redirect('users:usuarios_web')
            except requests.RequestException as e:
                if e.response is not None:
                    try:
                        detail = e.response.json().get('detail', str(e))
                    except:
                        detail = str(e)
                    messages.error(request, f"Error al crear usuario: {detail}")
                else:
                    messages.error(request, f"Error de conexión: {str(e)}")
    else:
        form = SimpleUserForm()

    return render(request, 'usuarios_web/create.html', {'form': form})


@admin_required
def editar_usuario_web(request, user_id):
    """Editar usuario web existente"""
    # Primero obtenemos el usuario actual para llenar el formulario
    # Podríamos usar la API para esto también
    try:
        response = requests.get(f"{API_URL}/users/{user_id}")
        response.raise_for_status()
        user_data = response.json()

        # Verificar que pertenece a la misma asociación (seguridad básica en frontend, backend ya valida)
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

    # Usamos el User model de Django solo para inicializar el ModelForm si es necesario,
    # pero como EditUserForm es un ModelForm, espera una instancia.
    # Truco: Pasamos initial data y no instance, o creamos una instancia dummy.
    # Mejor: Modificar el formulario para que no sea ModelForm o usarlo sin instance para validación.
    # Pero EditUserForm(instance=...) se usa para poblar.
    # Vamos a usar initial=initial_data.

    if request.method == 'POST':
        # Usamos el form para validación de campos
        form = EditUserForm(request.POST)
        # Hack: EditUserForm es ModelForm, requiere instance para update, pero aquí queremos validar datos.
        # Si no pasamos instance, valida unique constraints contra la DB local de Django (que sigue existiendo).
        # Esto es bueno: valida contra la DB local que es la misma que la del backend.
        # Pero necesitamos pasar el ID para que excluya al usuario actual de la validación de unique.
        # Como estamos en transición, podemos obtener el objeto local para el form.
        user_obj = get_object_or_404(User, id=user_id)
        form = EditUserForm(request.POST, instance=user_obj)

        if form.is_valid():
            update_data = {
                "first_name": form.cleaned_data['first_name'],
                "last_name": form.cleaned_data['last_name'],
                "email": form.cleaned_data['email'],
                "role": form.cleaned_data['role'],
                # is_active no está en UserUpdate schema del backend aun, vamos a añadirlo o ignorarlo
                # El schema UserUpdate tiene: first_name, last_name, email, role, telefono, direccion
            }

            try:
                response = requests.put(f"{API_URL}/users/{user_id}", json=update_data)
                response.raise_for_status()
                messages.success(request, f"Usuario {user_data['username']} actualizado.")
                return redirect('users:usuarios_web')
            except requests.RequestException as e:
                messages.error(request, f"Error al actualizar: {str(e)}")
    else:
        # Para GET, necesitamos el objeto local para que el ModelForm renderice bien (si usamos instance)
        # O usamos initial.
        user_obj = get_object_or_404(User, id=user_id)
        form = EditUserForm(instance=user_obj)

    return render(request, 'usuarios_web/edit.html', {'form': form, 'user_obj': user_data})


@admin_required
def eliminar_usuario_web(request, user_id):
    """Eliminar usuario web"""
    # Obtener datos para mostrar confirmación
    try:
        response = requests.get(f"{API_URL}/users/{user_id}")
        response.raise_for_status()
        user_data = response.json()
    except:
        messages.error(request, "Usuario no encontrado")
        return redirect('users:usuarios_web')

    if request.method == 'POST':
        try:
            response = requests.delete(f"{API_URL}/users/{user_id}")
            response.raise_for_status()
            messages.success(request, f"Usuario {user_data['username']} eliminado.")
            return redirect('users:usuarios_web')
        except requests.RequestException as e:
             messages.error(request, f"Error al eliminar: {str(e)}")

    return render(request, 'usuarios_web/delete.html', {'user_obj': user_data})