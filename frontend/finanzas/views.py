"""
Vistas para gestión de finanzas/transacciones con CRUD completo
"""
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
import openpyxl
from datetime import datetime, timedelta
import requests

from users.utils import is_association_admin, association_required
from core.api import get_client
from .forms import TransaccionForm
from .models import Transaccion # Import needed for Form but not for querying

@login_required
@association_required
def list_transacciones(request):
    """Listar transacciones consumiendo la API"""
    asociacion_id = request.user.profile.asociacion.id
    client = get_client(request)

    # Parámetros de filtrado
    search = request.GET.get('search', '')
    tipo = request.GET.get('tipo', '')
    entidad = request.GET.get('entidad', '')
    year = request.GET.get('year', '')
    sort = request.GET.get('sort', '-fecha_transaccion')
    page_number = request.GET.get('page', 1)

    try:
        transacciones_data = client.get(f"finanzas/?asociacion_id={asociacion_id}") or []
    except requests.RequestException as e:
        messages.error(request, f"Error al conectar con el servidor: {str(e)}")
        transacciones_data = []

    # Procesar datos (convertir fechas, números)
    processed_transacciones = []
    for t in transacciones_data:
        try:
            t['fecha_transaccion'] = datetime.strptime(t['fecha_transaccion'], '%Y-%m-%d').date()
            t['cantidad'] = float(t['cantidad'])
            processed_transacciones.append(t)
        except (ValueError, TypeError):
            continue

    # Filtrado en memoria
    filtered_transacciones = []
    for t in processed_transacciones:
        # Búsqueda
        if search:
            search_lower = search.lower()
            if not (search_lower in t['concepto'].lower() or 
                    (t['descripcion'] and search_lower in t['descripcion'].lower()) or 
                    (t['entidad'] and search_lower in t['entidad'].lower())):
                continue
        
        # Tipo
        if tipo == 'ingreso' and t['cantidad'] < 0:
            continue
        if tipo == 'gasto' and t['cantidad'] > 0:
            continue

        # Entidad
        if entidad and entidad.lower() not in (t.get('entidad') or '').lower():
            continue

        # Año
        if year and t['fecha_transaccion'].year != int(year):
            continue

        filtered_transacciones.append(t)

    # Ordenamiento
    reverse = sort.startswith('-')
    sort_key = sort.lstrip('-')
    filtered_transacciones.sort(key=lambda x: x.get(sort_key) or '', reverse=reverse)

    # Paginación
    paginator = Paginator(filtered_transacciones, 20)
    page_obj = paginator.get_page(page_number)

    # Estadísticas
    total_ingresos = sum(t['cantidad'] for t in processed_transacciones if t['cantidad'] > 0)
    total_gastos = sum(abs(t['cantidad']) for t in processed_transacciones if t['cantidad'] < 0)
    balance = total_ingresos - total_gastos

    ingresos_filtrados = sum(t['cantidad'] for t in filtered_transacciones if t['cantidad'] > 0)
    gastos_filtrados = sum(abs(t['cantidad']) for t in filtered_transacciones if t['cantidad'] < 0)

    # Listas para filtros
    years_disponibles = sorted(list(set(t['fecha_transaccion'].year for t in processed_transacciones)), reverse=True)
    entidades_disponibles = sorted(list(set(t['entidad'] for t in processed_transacciones if t.get('entidad'))))

    # Gráficas
    # Agrupar datos para gráficas (usando filtered_transacciones para reflejar filtros)
    # Solo consideramos gastos para las gráficas de análisis de gastos
    gastos_para_graficas = [t for t in filtered_transacciones if t['cantidad'] < 0]
    
    # 1. Evolución Mensual
    monthly_data = {}
    for t in gastos_para_graficas:
        month_key = t['fecha_transaccion'].strftime('%Y-%m')
        monthly_data[month_key] = monthly_data.get(month_key, 0) + abs(t['cantidad'])
    
    monthly_labels = sorted(monthly_data.keys())
    monthly_values = [monthly_data[k] for k in monthly_labels]

    # 2. Por Proyecto
    project_data = {}
    for t in gastos_para_graficas:
        # Usamos ID como label temporalmente, idealmente sería el nombre
        project_key = f"Proyecto {t['proyecto_id']}" if t['proyecto_id'] else "Sin Proyecto"
        project_data[project_key] = project_data.get(project_key, 0) + abs(t['cantidad'])
    
    project_labels = list(project_data.keys())
    project_values = [project_data[k] for k in project_labels]

    # 3. Por Entidad
    entity_data = {}
    for t in gastos_para_graficas:
        entity_key = t['entidad'] or "Sin Entidad"
        entity_data[entity_key] = entity_data.get(entity_key, 0) + abs(t['cantidad'])
    
    entity_labels = list(entity_data.keys())
    entity_values = [entity_data[k] for k in entity_labels]

    # 4. Por Año (Nuevo)
    annual_data = {}
    for t in gastos_para_graficas:
        year_key = str(t['fecha_transaccion'].year)
        annual_data[year_key] = annual_data.get(year_key, 0) + abs(t['cantidad'])
    
    annual_labels = sorted(annual_data.keys())
    annual_values = [annual_data[k] for k in annual_labels]

    chart_data = json.dumps({
        'monthly': {'labels': monthly_labels, 'data': monthly_values},
        'project': {'labels': project_labels, 'data': project_values},
        'entity': {'labels': entity_labels, 'data': entity_values},
        'annual': {'labels': annual_labels, 'data': annual_values}
    })

    context = {
        'section': 'contabilidad',
        'asociacion': request.user.profile.asociacion,
        'is_admin': is_association_admin(request.user),
        'transacciones': page_obj,
        'page_obj': page_obj,
        'current_search': search,
        'current_tipo': tipo,
        'current_entidad': entidad,
        'current_year': year,
        'current_sort': sort,
        'total_transacciones': len(filtered_transacciones),
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'balance': balance,
        'ingresos_filtrados': ingresos_filtrados,
        'gastos_filtrados': gastos_filtrados,
        'years_disponibles': years_disponibles,
        'entidades_disponibles': entidades_disponibles,
        'chart_data': chart_data
    }

    return render(request, 'contabilidad/list.html', context)

@login_required
@association_required
def create_transaccion(request):
    """Crear transacción consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('finanzas:dashboard')

    if request.method == 'POST':
        form = TransaccionForm(request.POST, request.FILES, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "asociacion_id": request.user.profile.asociacion.id,
                "cantidad": float(data['cantidad']),
                "concepto": data['concepto'],
                "descripcion": data['descripcion'],
                "fecha_transaccion": data['fecha_transaccion'].isoformat(),
                "fecha_vencimiento": data['fecha_vencimiento'].isoformat() if data['fecha_vencimiento'] else None,
                "entidad": data['entidad'],
                "evento_id": data['evento'].id if data['evento'] else None,
                "proyecto_id": data['proyecto'].id if data['proyecto'] else None,
                "socia_id": data['socia'].id if data['socia'] else None,
            }

            client = get_client(request)
            try:
                # 1. Crear transacción
                response = client.post("finanzas/", data=payload)
                
                # 2. Subir archivo si existe
                if 'comprobante' in request.FILES and response and 'id' in response:
                    uploaded_file = request.FILES['comprobante']
                    files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}
                    file_data = {
                        'asociacion_id': request.user.profile.asociacion.id,
                        'transaction_id': response['id']
                    }
                    # Nota: Este endpoint de drive debe existir y funcionar
                    client.post('drive/upload-transaction-file', data=file_data, files=files)

                messages.success(request, "Transacción creada exitosamente.")
                return redirect('finanzas:dashboard')
            except requests.RequestException as e:
                messages.error(request, f"Error al crear transacción: {str(e)}")
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = TransaccionForm(asociacion=request.user.profile.asociacion)

    context = {
        'section': 'contabilidad',
        'title': 'Nueva Transacción',
        'form': form
    }
    return render(request, 'contabilidad/create.html', context)

@login_required
@association_required
def update_transaccion(request, pk):
    """Actualizar transacción consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('finanzas:dashboard')

    client = get_client(request)
    try:
        t_data = client.get(f"finanzas/{pk}")
    except requests.RequestException:
        messages.error(request, "Error al obtener datos.")
        return redirect('finanzas:dashboard')

    # Crear instancia temporal
    t_instance = Transaccion(
        id=t_data['id'],
        cantidad=t_data['cantidad'],
        concepto=t_data['concepto'],
        descripcion=t_data['descripcion'],
        entidad=t_data['entidad'],
        drive_file_id=t_data.get('drive_file_id'),
        drive_file_name=t_data.get('drive_file_name'),
        drive_file_link=t_data.get('drive_file_link'),
        asociacion_id=t_data['asociacion_id']
    )
    # Fechas
    if t_data.get('fecha_transaccion'):
        t_instance.fecha_transaccion = datetime.strptime(t_data['fecha_transaccion'], '%Y-%m-%d').date()
    if t_data.get('fecha_vencimiento'):
        t_instance.fecha_vencimiento = datetime.strptime(t_data['fecha_vencimiento'], '%Y-%m-%d').date()
    
    # FKs (Solo IDs para el formulario, aunque ModelForm querrá objetos)
    # Para que ModelForm funcione bien con initial, necesitamos pasar los IDs
    # Pero ModelForm espera instancias en instance.fk.
    # Hack: Asignar IDs a los campos _id
    t_instance.evento_id = t_data.get('evento_id')
    t_instance.proyecto_id = t_data.get('proyecto_id')
    t_instance.socia_id = t_data.get('socia_id')

    if request.method == 'POST':
        form = TransaccionForm(request.POST, request.FILES, instance=t_instance, asociacion=request.user.profile.asociacion)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "cantidad": float(data['cantidad']),
                "concepto": data['concepto'],
                "descripcion": data['descripcion'],
                "fecha_transaccion": data['fecha_transaccion'].isoformat(),
                "fecha_vencimiento": data['fecha_vencimiento'].isoformat() if data['fecha_vencimiento'] else None,
                "entidad": data['entidad'],
                "evento_id": data['evento'].id if data['evento'] else None,
                "proyecto_id": data['proyecto'].id if data['proyecto'] else None,
                "socia_id": data['socia'].id if data['socia'] else None,
            }

            try:
                client.put(f"finanzas/{pk}", data=payload)
                
                # Subir archivo si existe
                if 'comprobante' in request.FILES:
                    uploaded_file = request.FILES['comprobante']
                    files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}
                    file_data = {
                        'asociacion_id': request.user.profile.asociacion.id,
                        'transaction_id': pk
                    }
                    client.post('drive/upload-transaction-file', data=file_data, files=files)

                messages.success(request, "Transacción actualizada.")
                return redirect('finanzas:dashboard')
            except requests.RequestException as e:
                messages.error(request, f"Error al actualizar: {str(e)}")
        else:
            messages.error(request, "Corrige los errores.")
    else:
        form = TransaccionForm(instance=t_instance, asociacion=request.user.profile.asociacion)

    context = {
        'section': 'contabilidad',
        'title': f"Editar: {t_data['concepto']}",
        'form': form,
        'object': t_instance
    }
    return render(request, 'contabilidad/edit.html', context)

@login_required
@association_required
def delete_transaccion(request, pk):
    """Eliminar transacción consumiendo la API"""
    if not is_association_admin(request.user):
        messages.error(request, "No tienes permisos.")
        return redirect('finanzas:dashboard')

    client = get_client(request)
    try:
        t_data = client.get(f"finanzas/{pk}")
    except requests.RequestException:
        messages.error(request, "Error al obtener datos.")
        return redirect('finanzas:dashboard')

    if request.method == 'POST':
        try:
            client.delete(f"finanzas/{pk}")
            messages.success(request, "Transacción eliminada.")
            return redirect('finanzas:dashboard')
        except requests.RequestException as e:
            messages.error(request, f"Error al eliminar: {str(e)}")

    t_obj = type('obj', (object,), t_data)

    context = {
        'section': 'contabilidad',
        'title': f"Eliminar: {t_data['concepto']}",
        'object': t_obj
    }
    return render(request, 'contabilidad/delete.html', context)

@login_required
@association_required
def download_report(request):
    """Descargar informe de transacciones en Excel"""
    asociacion_id = request.user.profile.asociacion.id
    client = get_client(request)
    
    # Obtener todas las transacciones (sin paginación)
    try:
        transacciones_data = client.get(f"finanzas/?asociacion_id={asociacion_id}") or []
    except requests.RequestException:
        transacciones_data = []

    # Crear libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transacciones"

    # Encabezados
    headers = ['Fecha', 'Concepto', 'Tipo', 'Cantidad', 'Entidad', 'Proyecto', 'Evento', 'Socia']
    ws.append(headers)

    # Datos
    for t in transacciones_data:
        tipo = "Ingreso" if t['cantidad'] > 0 else "Gasto"
        row = [
            t['fecha_transaccion'],
            t['concepto'],
            tipo,
            t['cantidad'],
            t['entidad'] or '',
            t['proyecto_id'] or '', # Idealmente mostrar nombre
            t['evento_id'] or '',   # Idealmente mostrar nombre
            t['socia_id'] or ''     # Idealmente mostrar nombre
        ]
        ws.append(row)

    # Preparar respuesta
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=transacciones_{datetime.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response

