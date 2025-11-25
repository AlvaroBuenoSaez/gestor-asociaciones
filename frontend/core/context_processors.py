from django.conf import settings
import os

def global_settings(request):
    """
    Context processor para exponer variables de configuración globales a los templates.
    """
    # Intentar obtener de settings, si no, de variables de entorno directas
    key = getattr(settings, 'GEOAPIFY_API_KEY', None)
    if not key:
        key = os.getenv('GEOAPIFY_API_KEY', '')

    return {
        'GEOAPIFY_API_KEY': key,
        'GEOAPIFY_BIAS_LAT': getattr(settings, 'GEOAPIFY_BIAS_LAT', '40.416775'),
        'GEOAPIFY_BIAS_LON': getattr(settings, 'GEOAPIFY_BIAS_LON', '-3.703790'),
        'GEOAPIFY_COUNTRY_CODE': getattr(settings, 'GEOAPIFY_COUNTRY_CODE', 'es'),
    }
