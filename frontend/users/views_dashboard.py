"""
Vistas para el dashboard principal
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import association_required
from core.api import get_client


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


@association_required
def drive_config(request):
    client = get_client(request)
    asociacion = request.user.profile.asociacion

    # Verificar estado de conexión
    try:
        config_status = client.get(f'drive/config/{asociacion.id}')
        is_connected = config_status.get('is_connected', False)
        folder_link = config_status.get('folder_link')
    except Exception:
        is_connected = False
        folder_link = None

    if request.method == 'POST':
        # Crear nueva carpeta
        if 'create_folder' in request.POST:
            folder_name = request.POST.get('folder_name', 'Gestor Asociaciones')
            try:
                response = client.post('drive/create-folder', data={
                    'asociacion_id': asociacion.id,
                    'folder_name': folder_name
                })
                if response and 'folder' in response:
                    asociacion.drive_folder_id = response['folder']['id']
                    asociacion.save()

                    # Intentar obtener el link si viene en la respuesta
                    new_folder_link = response['folder'].get('webViewLink')
                    if new_folder_link:
                        msg = f'Carpeta "{folder_name}" creada. <a href="{new_folder_link}" target="_blank">Abrir en Drive</a>'
                        messages.success(request, msg, extra_tags='safe')
                    else:
                        messages.success(request, f'Carpeta "{folder_name}" creada y configurada correctamente')
            except Exception as e:
                messages.error(request, f'Error al crear carpeta: {str(e)}')
            return redirect('users:drive_config')

        # Seleccionar carpeta existente (si hay permisos)
        folder_id = request.POST.get('folder_id')
        if folder_id:
            try:
                client.post('drive/config', data={
                    'asociacion_id': asociacion.id,
                    'folder_id': folder_id
                })
                asociacion.drive_folder_id = folder_id
                asociacion.save()
                messages.success(request, 'Carpeta de Drive configurada correctamente')
            except Exception as e:
                messages.error(request, f'Error al configurar Drive: {str(e)}')
        return redirect('users:drive_config')

    # Obtener URL de autorización si no está conectado
    auth_url = None
    if not is_connected:
        try:
            response = client.get('drive/auth/url')
            auth_url = response.get('url')
        except Exception:
            pass

    # Obtener carpetas si está conectado
    folders = []
    if is_connected:
        try:
            folders = client.get('drive/folders', params={'asociacion_id': asociacion.id})
        except Exception:
            pass

    return render(request, 'dashboard/drive_config.html', {
        'folders': folders,
        'asociacion': asociacion,
        'is_connected': is_connected,
        'auth_url': auth_url,
        'folder_link': folder_link
    })

@association_required
def drive_callback(request):
    """Maneja el retorno de Google tras la autorización"""
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        messages.error(request, f'Error en autorización de Google: {error}')
        return redirect('users:drive_config')

    if code:
        client = get_client(request)
        asociacion = request.user.profile.asociacion
        try:
            client.post('drive/auth/callback', data={
                'code': code,
                'asociacion_id': asociacion.id
            })
            messages.success(request, 'Google Drive conectado correctamente')
        except Exception as e:
            messages.error(request, f'Error al conectar Drive: {str(e)}')

    return redirect('users:drive_config')


@association_required
def drive_files(request):
    client = get_client(request)
    asociacion = request.user.profile.asociacion

    if request.method == 'POST' and request.FILES.get('file'):
        try:
            # Preparar archivo para envío
            uploaded_file = request.FILES['file']
            files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}

            client.post('drive/upload',
                        data={'asociacion_id': asociacion.id},
                        files=files
                        )
            messages.success(request, 'Archivo subido correctamente')
        except Exception as e:
            messages.error(request, f'Error al subir archivo: {str(e)}')
        return redirect('users:drive_files')

    if request.method == 'POST' and request.POST.get('delete_file_id'):
        try:
            file_id = request.POST.get('delete_file_id')
            client.delete(f'drive/files/{file_id}')
            messages.success(request, 'Archivo eliminado correctamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar archivo: {str(e)}')
        return redirect('users:drive_files')

    files = []
    if asociacion.drive_folder_id:
        try:
            files = client.get('drive/files', params={'asociacion_id': asociacion.id})
        except Exception:
            pass

    return render(request, 'dashboard/drive_files.html', {
        'files': files,
        'asociacion': asociacion
    })