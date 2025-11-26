"""
Vistas para gestión de socias consumiendo la API del backend
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from users.utils import association_required, is_association_admin
from .forms import SociaForm
from .models import Socia
from core.api import get_client
import requests

@login_required
@association_required
def list_socias(request):
    """Listar socias consumiendo la API"""
    asociacion_id = request.user.profile.asociacion.id
    client = get_client(request)

    # Parámetros de filtrado
    search = request.GET.get('search', '')
    pagado = request.GET.get('pagado', '')
    provincia = request.GET.get('provincia', '')
    sort = request.GET.get('sort', 'numero_socia')
    page_number = request.GET.get('page', 1)
    export_emails = request.GET.get('export_emails') == 'true'

    # Construir query params
    params = {
        'asociacion_id': asociacion_id,
        'skip': 0,
        'limit': 1000
    }

    try:
        socias_data = client.get("/socias/", params=params) or []
    except requests.RequestException as e:
        messages.error(request, f"Error al conectar con el servidor: {str(e)}")
        socias_data = []

    # Filtrado en memoria (Python)
    filtered_socias = []
    for s in socias_data:
        # Búsqueda general
        if search:
            search_lower = search.lower()
            if not (search_lower in str(s.get('numero_socia', '')).lower() or
                    search_lower in s.get('nombre', '').lower() or
                    search_lower in s.get('apellidos', '').lower() or
                    search_lower in s.get('telefono', '').lower() or
                    search_lower in s.get('direccion', '').lower()):
                continue

        # Filtro pagado
        if pagado == 'si' and not s.get('pagado'):
            continue
        if pagado == 'no' and s.get('pagado'):
            continue

        # Filtro provincia
        if provincia and provincia.lower() not in s.get('provincia', '').lower():
            continue

        filtered_socias.append(s)

    # Si se solicitan emails, devolver JSON
    if export_emails:
        from django.http import JsonResponse
        emails = [s.get('email') for s in filtered_socias if s.get('email')]
        return JsonResponse({'emails': emails})

    # Ordenamiento
    reverse = False
    sort_key = sort
    if sort.startswith('-'):
        reverse = True
        sort_key = sort[1:]

    filtered_socias.sort(key=lambda x: x.get(sort_key) or '', reverse=reverse)

    # Paginación
    paginator = Paginator(filtered_socias, 20)
    page_obj = paginator.get_page(page_number)

    # Estadísticas
    total_socias = len(filtered_socias)
    socias_pagadas = sum(1 for s in filtered_socias if s.get('pagado'))
    socias_pendientes = total_socias - socias_pagadas

    # Provincias disponibles
    provincias_disponibles = sorted(list(set(s.get('provincia') for s in socias_data if s.get('provincia'))))

    context = {
        'section': 'socias',
        'asociacion': request.user.profile.asociacion,
        'is_admin': is_association_admin(request.user),
        'socias': page_obj,
        'page_obj': page_obj,
        'current_search': search,
        'current_pagado': pagado,
        'current_provincia': provincia,
        'current_sort': sort,
        'total_socias': total_socias,
        'socias_pagadas': socias_pagadas,
        'socias_pendientes': socias_pendientes,
        'provincias_disponibles': provincias_disponibles
    }

    return render(request, 'socias/list.html', context)

@login_required
@association_required
def create_socia(request):
    """Crear socia consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('socias:list')

    if request.method == 'POST':
        form = SociaForm(request.POST, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "numero_socia": data['numero_socia'],
                "nombre": data['nombre'],
                "apellidos": data['apellidos'],
                "telefono": data['telefono'],
                "email": data.get('email'),
                "direccion": data['direccion'],
                "numero": data.get('numero'),
                "piso": data.get('piso'),
                "escalera": data.get('escalera'),
                "provincia": data['provincia'],
                "codigo_postal": data['codigo_postal'],
                "pais": data['pais'],
                "nacimiento": data['nacimiento'].isoformat() if data['nacimiento'] else None,
                "pagado": data['pagado'],
                "descripcion": data['descripcion'],
                "asociacion_id": request.user.profile.asociacion.id
            }

            client = get_client(request)
            try:
                client.post("/socias/", data=payload)
                messages.success(request, f"Socia {data['nombre']} creada exitosamente.")
                return redirect('socias:list')
            except requests.RequestException as e:
                detail = getattr(e, 'api_error', {}).get('detail', str(e))
                messages.error(request, f"Error al crear socia: {detail}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = SociaForm(asociacion=request.user.profile.asociacion)

    context = {
        'section': 'socias',
        'title': 'Nueva Socia',
        'form': form
    }
    return render(request, 'socias/create.html', context)

@login_required
@association_required
def update_socia(request, pk):
    """Actualizar socia consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('socias:list')

    client = get_client(request)
    try:
        socia_data = client.get(f"/socias/{pk}")
    except requests.RequestException:
        messages.error(request, "No se pudo recuperar la información de la socia.")
        return redirect('socias:list')

    # Crear instancia temporal para el formulario
    socia_instance = Socia(
        id=socia_data['id'],
        numero_socia=socia_data['numero_socia'],
        nombre=socia_data['nombre'],
        apellidos=socia_data['apellidos'],
        telefono=socia_data['telefono'],
        email=socia_data.get('email'),
        direccion=socia_data['direccion'],
        numero=socia_data.get('numero'),
        piso=socia_data.get('piso'),
        escalera=socia_data.get('escalera'),
        provincia=socia_data['provincia'],
        codigo_postal=socia_data['codigo_postal'],
        pais=socia_data['pais'],
        pagado=socia_data['pagado'],
        descripcion=socia_data['descripcion'],
        asociacion_id=socia_data['asociacion_id']
    )
    if socia_data.get('nacimiento'):
        from datetime import datetime
        try:
            socia_instance.nacimiento = datetime.fromisoformat(socia_data['nacimiento']).date()
        except ValueError:
            pass

    if request.method == 'POST':
        form = SociaForm(request.POST, instance=socia_instance, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "numero_socia": data['numero_socia'],
                "nombre": data['nombre'],
                "apellidos": data['apellidos'],
                "telefono": data['telefono'],
                "email": data.get('email'),
                "direccion": data['direccion'],
                "numero": data.get('numero'),
                "piso": data.get('piso'),
                "escalera": data.get('escalera'),
                "provincia": data['provincia'],
                "codigo_postal": data['codigo_postal'],
                "pais": data['pais'],
                "nacimiento": data['nacimiento'].isoformat() if data['nacimiento'] else None,
                "pagado": data['pagado'],
                "descripcion": data['descripcion'],
                "asociacion_id": request.user.profile.asociacion.id
            }

            try:
                client.put(f"/socias/{pk}", data=payload)
                messages.success(request, f"Socia {data['nombre']} actualizada exitosamente.")
                return redirect('socias:list')
            except requests.RequestException as e:
                detail = getattr(e, 'api_error', {}).get('detail', str(e))
                messages.error(request, f"Error al actualizar: {detail}")
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = SociaForm(instance=socia_instance, asociacion=request.user.profile.asociacion)

    context = {
        'section': 'socias',
        'title': f"Editar Socia: {socia_data['nombre']}",
        'form': form,
        'object': socia_instance
    }
    return render(request, 'socias/edit.html', context)

@login_required
@association_required
def delete_socia(request, pk):
    """Eliminar socia consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('socias:list')

    client = get_client(request)
    try:
        socia_data = client.get(f"/socias/{pk}")
    except requests.RequestException:
        messages.error(request, "Error al obtener datos.")
        return redirect('socias:list')

    if request.method == 'POST':
        try:
            client.delete(f"/socias/{pk}")
            messages.success(request, "Socia eliminada correctamente.")
            return redirect('socias:list')
        except requests.RequestException as e:
            messages.error(request, f"Error al eliminar: {str(e)}")

    socia_obj = type('obj', (object,), socia_data)

    context = {
        'section': 'socias',
        'title': f"Eliminar Socia: {socia_data['nombre']}",
        'object': socia_obj
    }
    return render(request, 'socias/delete.html', context)
