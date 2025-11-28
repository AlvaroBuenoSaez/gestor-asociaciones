"""
Vistas para autenticación (login, logout, registro)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from .models import AdminInvitation
from .forms import AdminRegistrationForm


@csrf_protect
@never_cache
def user_login(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('users:home')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido/a, {user.get_full_name() or user.username}!')

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('users:home')
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


def user_logout(request):
    """Vista de logout"""
    username = request.user.username if request.user.is_authenticated else None
    logout(request)
    if username:
        messages.success(request, f'¡Hasta luego, {username}!')
    return redirect('users:login')


def accept_invite(request, token):
    """Vista para aceptar invitación de administrador"""
    invitation = get_object_or_404(AdminInvitation, token=token)
    
    if not invitation.is_valid:
        messages.error(request, "Esta invitación ha expirado o ya ha sido usada.")
        return redirect('users:login')
        
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = invitation.email
            
            if invitation.asociacion:
                # Es un administrador de asociación (Dashboard)
                user.is_staff = False
                user.is_superuser = False
            else:
                # Es un superusuario (Admin Site)
                user.is_staff = True
                user.is_superuser = True
            
            user.save()
            
            # El perfil se crea automáticamente por la señal post_save
            if invitation.asociacion:
                profile = user.profile
                profile.asociacion = invitation.asociacion
                profile.role = 'admin'
                profile.save()
            
            invitation.used = True
            invitation.save()
            
            login(request, user)
            
            if user.is_superuser:
                messages.success(request, f"¡Bienvenido Superusuario {user.username}!")
                return redirect('admin:index')
            else:
                messages.success(request, f"¡Bienvenido/a {user.username}! Ahora eres administrador de {invitation.asociacion}.")
                return redirect('users:dashboard')
    else:
        form = AdminRegistrationForm()
        
    return render(request, 'auth/accept_invite.html', {'form': form, 'email': invitation.email})


def home(request):
    """Vista principal - redirige según el tipo de usuario"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    if request.user.is_superuser:
        return redirect('admin:index')  # Redirigir directamente al admin
    elif hasattr(request.user, 'profile') and request.user.profile.asociacion:
        return redirect('users:dashboard')
    else:
        messages.warning(request, 'Tu cuenta aún no tiene una asociación asignada. Contacta con el administrador.')
        return render(request, 'auth/no_association.html')