import requests
from django.conf import settings

# Idealmente esto vendría de settings
API_BASE_URL = getattr(settings, 'API_BASE_URL', "http://localhost:8000/api/v1")

class ApiClient:
    """Cliente para consumir la API del backend"""

    def __init__(self, request=None):
        self.request = request
        self.base_url = API_BASE_URL
        self.timeout = 10

    def _get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        # Futuro: Añadir token de autenticación del usuario
        return headers

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            # Si la respuesta está vacía (ej. 204 No Content), devolver None
            if not response.content:
                return None
            return response.json()
        except requests.RequestException as e:
            # Aquí podríamos añadir logging centralizado
            # Si la respuesta tiene detalles de error (JSON), podríamos parsearlos y adjuntarlos a la excepción
            if response.content:
                try:
                    error_detail = response.json()
                    e.api_error = error_detail
                except ValueError:
                    pass
            raise e

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(url, params=params, headers=self._get_headers(), timeout=self.timeout)
        return self._handle_response(response)

    def post(self, endpoint, data=None, files=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        if files:
            # Si hay archivos, requests se encarga del Content-Type multipart
            if 'Content-Type' in headers:
                del headers['Content-Type']
            response = requests.post(url, data=data, files=files, headers=headers, timeout=self.timeout)
        else:
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)

        return self._handle_response(response)

    def put(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.put(url, json=data, headers=self._get_headers(), timeout=self.timeout)
        return self._handle_response(response)

    def delete(self, endpoint):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.delete(url, headers=self._get_headers(), timeout=self.timeout)
        return self._handle_response(response)

def get_client(request=None):
    """Factory para obtener una instancia del cliente"""
    return ApiClient(request)
