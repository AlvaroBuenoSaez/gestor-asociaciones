"""
Vistas para gestión de eventos consumiendo la API del backend
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from users.utils import association_required, is_association_admin
from .forms import EventoForm
from .models import Evento
from core.api import get_client
import requests

@login_required
@association_required
def list_eventos(request):
    """Listar eventos consumiendo la API"""
    asociacion_id = request.user.profile.asociacion.id
    client = get_client(request)

    # Parámetros de filtrado
    search = request.GET.get('search', '')
    year = request.GET.get('year', '')
    order = request.GET.get('order', 'fecha')
    page_number = request.GET.get('page', 1)

    # Obtener eventos de la API
    try:
        eventos_data = client.get("/eventos/", params={'asociacion_id': asociacion_id}) or []
    except requests.RequestException as e:
        messages.error(request, f"Error al conectar con el servidor: {str(e)}")
        eventos_data = []

    # Filtrado en memoria
    filtered_eventos = []
    for e in eventos_data:
        # Búsqueda
        if search:
            search_lower = search.lower()
            if not (search_lower in e.get('nombre', '').lower() or
                    search_lower in e.get('descripcion', '').lower() or
                    search_lower in (e.get('lugar_nombre') or '').lower() or
                    search_lower in (e.get('lugar_direccion') or '').lower() or
                    search_lower in e.get('colaboradores', '').lower()):
                continue

        # Filtro año
        if year:
            fecha_str = e.get('fecha')
            if fecha_str and not fecha_str.startswith(year):
                continue

        filtered_eventos.append(e)

    # Ordenamiento
    reverse = False
    if order.startswith('-'):
        reverse = True
        order_key = order[1:]
    else:
        order_key = order

    # Mapeo de claves de ordenamiento
    key_map = {
        'fecha': 'fecha',
        'nombre': 'nombre'
    }
    sort_key = key_map.get(order_key, 'fecha')

    filtered_eventos.sort(key=lambda x: x.get(sort_key) or '', reverse=reverse)

    # Paginación
    paginator = Paginator(filtered_eventos, 20)
    page_obj = paginator.get_page(page_number)

    # Estadísticas
    total_eventos = len(eventos_data)

    # Años disponibles
    years = sorted(list(set(e.get('fecha')[:4] for e in eventos_data if e.get('fecha'))), reverse=True)

    context = {
        'section': 'actividades',
        'asociacion': request.user.profile.asociacion,
        'is_admin': is_association_admin(request.user),
        'eventos': page_obj,
        'page_obj': page_obj,
        'current_search': search,
        'current_year': year,
        'current_order': order,
        'total_eventos': total_eventos,
        'filtered_count': len(filtered_eventos),
        'years': years
    }

    return render(request, 'actividades/list.html', context)

@login_required
@association_required
def create_evento(request):
    """Crear evento consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('eventos:list')

    if request.method == 'POST':
        form = EventoForm(request.POST, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            # Preparar payload
            payload = {
                "nombre": data['nombre'],
                "descripcion": data['descripcion'],
                "lugar_nombre": data['lugar_nombre'],
                "lugar_direccion": data['lugar_direccion'],
                "fecha": data['fecha'].isoformat() if data['fecha'] else None,
                "duracion": str(data['duracion']) if data['duracion'] else None,
                "colaboradores": data['colaboradores'],
                "observaciones": data['observaciones'],
                "asociacion_id": request.user.profile.asociacion.id,
                "responsable_id": data['responsable'].id if data['responsable'] else None,
                "proyecto_id": data['proyecto'].id if data.get('proyecto') else None
            }

            # Ajuste para duracion
            if data['duracion']:
                payload['duracion'] = data['duracion'].total_seconds()

            client = get_client(request)
            try:
                client.post("/eventos/", data=payload)
                messages.success(request, f"Evento {data['nombre']} creado exitosamente.")
                return redirect('eventos:list')
            except requests.RequestException as e:
                detail = getattr(e, 'api_error', {}).get('detail', str(e))
                messages.error(request, f"Error al crear evento: {detail}")
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = EventoForm(asociacion=request.user.profile.asociacion)

    context = {
        'section': 'actividades',
        'title': 'Nuevo Evento',
        'form': form
    }
    return render(request, 'actividades/create.html', context)

@login_required
@association_required
def update_evento(request, pk):
    """Actualizar evento consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('eventos:list')

    client = get_client(request)
    # Obtener datos
    try:
        evento_data = client.get(f"/eventos/{pk}")
    except requests.RequestException:
        messages.error(request, "Error al obtener datos.")
        return redirect('eventos:list')

    # Crear instancia dummy para form
    from datetime import datetime, timedelta
    from socias.models import Socia
    from proyectos.models import Proyecto

    responsable_obj = None
    if evento_data.get('responsable_id'):
        try:
            responsable_obj = Socia.objects.get(id=evento_data['responsable_id'])
        except Socia.DoesNotExist:
            pass

    proyecto_obj = None
    if evento_data.get('proyecto_id'):
        try:
            proyecto_obj = Proyecto.objects.get(id=evento_data['proyecto_id'])
        except Proyecto.DoesNotExist:
            pass

    evento_instance = Evento(
        id=evento_data['id'],
        nombre=evento_data['nombre'],
        descripcion=evento_data['descripcion'],
        lugar_nombre=evento_data.get('lugar_nombre'),
        lugar_direccion=evento_data.get('lugar_direccion'),
        colaboradores=evento_data['colaboradores'],
        observaciones=evento_data['observaciones'],
        asociacion_id=evento_data['asociacion_id'],
        responsable=responsable_obj,
        proyecto=proyecto_obj
    )

    if evento_data.get('fecha'):
        try:
            evento_instance.fecha = datetime.fromisoformat(evento_data['fecha'])
        except ValueError:
            pass

    if evento_data.get('duracion'):
        if isinstance(evento_data['duracion'], (int, float)):
             evento_instance.duracion = timedelta(seconds=evento_data['duracion'])

    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento_instance, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "nombre": data['nombre'],
                "descripcion": data['descripcion'],
                "lugar_nombre": data['lugar_nombre'],
                "lugar_direccion": data['lugar_direccion'],
                "fecha": data['fecha'].isoformat() if data['fecha'] else None,
                "duracion": data['duracion'].total_seconds() if data['duracion'] else None,
                "colaboradores": data['colaboradores'],
                "observaciones": data['observaciones'],
                "responsable_id": data['responsable'].id if data['responsable'] else None,
                "proyecto_id": data['proyecto'].id if data.get('proyecto') else None
            }

            try:
                client.put(f"/eventos/{pk}", data=payload)
                messages.success(request, f"Evento {data['nombre']} actualizado.")
                return redirect('eventos:list')
            except requests.RequestException as e:
                detail = getattr(e, 'api_error', {}).get('detail', str(e))
                messages.error(request, f"Error al actualizar: {detail}")
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = EventoForm(instance=evento_instance, asociacion=request.user.profile.asociacion)

    context = {
        'section': 'actividades',
        'title': f"Editar: {evento_data['nombre']}",
        'form': form,
        'object': evento_instance
    }
    return render(request, 'actividades/edit.html', context)

@login_required
@association_required
def delete_evento(request, pk):
    """Eliminar evento consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('eventos:list')

    client = get_client(request)
    try:
        evento_data = client.get(f"/eventos/{pk}")
    except requests.RequestException:
        messages.error(request, "Error al obtener datos.")
        return redirect('eventos:list')

    if request.method == 'POST':
        try:
            client.delete(f"/eventos/{pk}")
            messages.success(request, "Evento eliminado.")
            return redirect('eventos:list')
        except requests.RequestException as e:
            messages.error(request, f"Error al eliminar: {str(e)}")

    # Preparar datos para el template
    # Inyectamos la asociación actual para que el template pueda acceder a object.asociacion.nombre
    evento_data['asociacion'] = request.user.profile.asociacion

    context = {
        'section': 'actividades',
        'title': f"Eliminar: {evento_data['nombre']}",
        'object': evento_data
    }
    return render(request, 'actividades/delete.html', context)

@association_required
def mapas(request):
    """Vista de mapas del barrio"""
    context = {
        'section': 'mapas',
        'asociacion': request.user.profile.asociacion,
    }
    return render(request, 'mapas/viewer.html', context)

@login_required
@association_required
def search_lugares(request):
    """Proxy para buscar lugares en el backend"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)

    client = get_client(request)
    asociacion_id = request.user.profile.asociacion.id
    try:
        # Llamada al backend
        lugares = client.get("/lugares/buscar", params={'q': query, 'asociacion_id': asociacion_id})
        return JsonResponse(lugares or [], safe=False)
    except requests.RequestException:
        return JsonResponse([], safe=False)
