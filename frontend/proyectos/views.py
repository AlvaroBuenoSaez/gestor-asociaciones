"""
Vistas para gestión de proyectos consumiendo la API
"""
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import datetime
import requests

from users.utils import is_association_admin, association_required
from core.api import get_client
from .forms import ProyectoForm
from .models import Proyecto # Import needed for Form

@login_required
@association_required
def list_proyectos(request):
    asociacion_id = request.user.profile.asociacion.id
    client = get_client(request)

    search = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    recursivo = request.GET.get('recursivo', '')
    order = request.GET.get('order', '-fecha_inicio')
    page_number = request.GET.get('page', 1)

    try:
        proyectos_data = client.get(f"proyectos/?asociacion_id={asociacion_id}") or []
    except requests.RequestException as e:
        messages.error(request, f"Error al conectar con el servidor: {str(e)}")
        proyectos_data = []

    # Process data
    processed_proyectos = []
    today = datetime.now().date()

    for p in proyectos_data:
        try:
            p['fecha_inicio'] = datetime.strptime(p['fecha_inicio'], '%Y-%m-%d').date()
            if p.get('fecha_final'):
                p['fecha_final'] = datetime.strptime(p['fecha_final'], '%Y-%m-%d').date()

            # Calculate state
            if today < p['fecha_inicio']:
                p['estado'] = 'pendiente'
                p['estado_display'] = '⏳ Pendiente'
            elif p.get('fecha_final') and today > p['fecha_final']:
                p['estado'] = 'finalizado'
                p['estado_display'] = '✅ Finalizado'
            else:
                p['estado'] = 'en_curso'
                p['estado_display'] = '🔄 En Curso'

            processed_proyectos.append(p)
        except (ValueError, TypeError):
            continue

    # Filter
    filtered_proyectos = []
    for p in processed_proyectos:
        if search:
            search_lower = search.lower()
            if not (search_lower in p['nombre'].lower() or
                    (p['descripcion'] and search_lower in p['descripcion'].lower()) or
                    (p.get('lugar') and search_lower in p['lugar'].lower())):
                continue

        if estado and p['estado'] != estado:
            continue

        if recursivo == 'si' and not p['recursivo']:
            continue
        if recursivo == 'no' and p['recursivo']:
            continue

        filtered_proyectos.append(p)

    # Sort
    reverse = order.startswith('-')
    sort_key = order.lstrip('-')
    filtered_proyectos.sort(key=lambda x: x.get(sort_key) or '', reverse=reverse)

    # Pagination
    paginator = Paginator(filtered_proyectos, 20)
    page_obj = paginator.get_page(page_number)

    # Stats
    total_proyectos = len(processed_proyectos)
    pendientes = sum(1 for p in processed_proyectos if p['estado'] == 'pendiente')
    en_curso = sum(1 for p in processed_proyectos if p['estado'] == 'en_curso')
    finalizados = sum(1 for p in processed_proyectos if p['estado'] == 'finalizado')
    recursivos = sum(1 for p in processed_proyectos if p['recursivo'])

    context = {
        'section': 'proyectos',
        'asociacion': request.user.profile.asociacion,
        'is_admin': is_association_admin(request.user),
        'proyectos': page_obj,
        'page_obj': page_obj,
        'current_search': search,
        'current_estado': estado,
        'current_recursivo': recursivo,
        'current_order': order,
        'total_proyectos': total_proyectos,
        'proyectos_pendientes': pendientes,
        'proyectos_en_curso': en_curso,
        'proyectos_finalizados': finalizados,
        'proyectos_recursivos': recursivos,
        'filtered_count': len(filtered_proyectos),
        'estados': [('pendiente', 'Pendiente'), ('en_curso', 'En Curso'), ('finalizado', 'Finalizado')],
        'recursivo_choices': [('si', 'Sí'), ('no', 'No')]
    }

    return render(request, 'proyectos/list.html', context)

@login_required
@association_required
def create_proyecto(request):
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('proyectos:list')

    if request.method == 'POST':
        form = ProyectoForm(request.POST, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "asociacion_id": request.user.profile.asociacion.id,
                "nombre": data['nombre'],
                "responsable_id": data['responsable'].id if data['responsable'] else None,
                "descripcion": data['descripcion'],
                "lugar_fk_id": data['lugar_fk'].id if data['lugar_fk'] else None,
                "fecha_inicio": data['fecha_inicio'].isoformat(),
                "fecha_final": data['fecha_final'].isoformat() if data['fecha_final'] else None,
                "recursivo": data['recursivo'],
            }

            client = get_client(request)
            try:
                response = client.post("proyectos/", data=payload)

                # Hybrid approach: Save M2M relationships using Django ORM
                if response and 'id' in response:
                    new_id = response['id']
                    try:
                        p_obj = Proyecto.objects.get(id=new_id)
                        p_obj.socias_involucradas.set(data['socias_involucradas'])
                        p_obj.personas_involucradas.set(data['personas_involucradas'])
                        p_obj.materiales_necesarios.set(data['materiales_necesarios'])
                    except Proyecto.DoesNotExist:
                        pass

                messages.success(request, f"Proyecto {data['nombre']} creado exitosamente.")
                return redirect('proyectos:list')
            except requests.RequestException as e:
                messages.error(request, f"Error al crear proyecto: {str(e)}")
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = ProyectoForm(asociacion=request.user.profile.asociacion)

    context = {
        'section': 'proyectos',
        'title': 'Nuevo Proyecto',
        'form': form
    }
    return render(request, 'proyectos/create.html', context)

@login_required
@association_required
def update_proyecto(request, pk):
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('proyectos:list')

    # Use ORM to get the object for the form (to populate M2M correctly)
    try:
        real_obj = Proyecto.objects.get(id=pk, asociacion=request.user.profile.asociacion)
    except Proyecto.DoesNotExist:
        messages.error(request, "Proyecto no encontrado.")
        return redirect('proyectos:list')

    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=real_obj, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "nombre": data['nombre'],
                "responsable_id": data['responsable'].id if data['responsable'] else None,
                "descripcion": data['descripcion'],
                "lugar_fk_id": data['lugar_fk'].id if data['lugar_fk'] else None,
                "fecha_inicio": data['fecha_inicio'].isoformat(),
                "fecha_final": data['fecha_final'].isoformat() if data['fecha_final'] else None,
                "recursivo": data['recursivo']
            }

            client = get_client(request)
            try:
                client.put(f"proyectos/{pk}", data=payload)

                # Update M2M relationships via ORM
                real_obj.socias_involucradas.set(data['socias_involucradas'])
                real_obj.personas_involucradas.set(data['personas_involucradas'])
                real_obj.materiales_necesarios.set(data['materiales_necesarios'])

                messages.success(request, "Proyecto actualizado.")
                return redirect('proyectos:list')
            except requests.RequestException as e:
                messages.error(request, f"Error al actualizar: {str(e)}")
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = ProyectoForm(instance=real_obj, asociacion=request.user.profile.asociacion)

    context = {
        'section': 'proyectos',
        'title': f"Editar: {real_obj.nombre}",
        'form': form,
        'object': real_obj
    }
    return render(request, 'proyectos/edit.html', context)

@login_required
@association_required
def delete_proyecto(request, pk):
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('proyectos:list')

    client = get_client(request)
    try:
        p_data = client.get(f"proyectos/{pk}")
    except requests.RequestException:
        messages.error(request, "Error al obtener datos.")
        return redirect('proyectos:list')

    if request.method == 'POST':
        try:
            client.delete(f"proyectos/{pk}")
            messages.success(request, "Proyecto eliminado.")
            return redirect('proyectos:list')
        except requests.RequestException as e:
            messages.error(request, f"Error al eliminar: {str(e)}")

    p_obj = type('obj', (object,), p_data)

    context = {
        'section': 'proyectos',
        'title': f"Eliminar: {p_data['nombre']}",
        'object': p_obj
    }
    return render(request, 'proyectos/delete.html', context)
