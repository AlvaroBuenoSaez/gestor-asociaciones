"""
Vistas para autenticación (login, logout, registro)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from .models import AdminInvitation
from .forms import AdminRegistrationForm, PasswordResetRequestForm


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


def password_reset_request(request):
    """Vista para solicitar restablecimiento de contraseña"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            # Buscar por username o email
            user = User.objects.filter(Q(username=identifier) | Q(email=identifier)).first()

            if user and user.email:
                # Guardar ID en sesión para mostrar el email enmascarado en el siguiente paso
                request.session['reset_user_id'] = user.id
                return redirect('users:password_reset_confirm_send')
            else:
                messages.error(request, "No se encontró un usuario con ese nombre o correo electrónico.")
    else:
        form = PasswordResetRequestForm()

    return render(request, 'auth/password_reset_request.html', {'form': form})


def password_reset_confirm_send(request):
    """Vista para confirmar el envío del correo con el email enmascarado"""
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('users:password_reset_request')

    user = get_object_or_404(User, id=user_id)

    # Enmascarar email: e*************@gmail.com
    email_parts = user.email.split('@')
    if len(email_parts) == 2:
        username_part = email_parts[0]
        domain_part = email_parts[1]
        if len(username_part) > 1:
            masked_username = username_part[0] + '*' * (len(username_part) - 1)
        else:
            masked_username = username_part
        masked_email = f"{masked_username}@{domain_part}"
    else:
        masked_email = user.email

    if request.method == 'POST':
        # Enviar correo
        subject = "Restablecer contraseña - Gestor Asociaciones"
        email_template_name = "auth/password_reset_email.html"
        c = {
            "email": user.email,
            'domain': request.META['HTTP_HOST'],
            'site_name': 'Gestor Asociaciones',
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http',
        }
        email_content = render_to_string(email_template_name, c)

        try:
            send_mail(
                subject,
                email_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=email_content # Enviar como HTML también
            )
            # Limpiar sesión
            if 'reset_user_id' in request.session:
                del request.session['reset_user_id']
            return redirect('users:password_reset_done')
        except Exception as e:
             print(f"Error enviando correo: {e}")
             messages.error(request, "Error al enviar el correo. Por favor inténtalo más tarde.")

    return render(request, 'auth/password_reset_confirm_send.html', {'masked_email': masked_email})


def password_reset_done(request):
    """Vista de confirmación de envío"""
    return render(request, 'auth/password_reset_done.html')


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