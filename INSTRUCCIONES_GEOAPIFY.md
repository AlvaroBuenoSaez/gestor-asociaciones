# Instrucciones de Configuración de Geoapify

Para habilitar el autocompletado de direcciones en los formularios de creación y edición de socias, es necesario configurar una API Key de Geoapify.

## Pasos para obtener la API Key

1.  **Registrarse**: Ve a [Geoapify](https://www.geoapify.com/) y regístrate para obtener una cuenta gratuita.
2.  **Crear Proyecto**: Una vez dentro del panel de control, crea un nuevo proyecto.
3.  **Obtener Key**: Copia la "API Key" generada para tu proyecto.

## Configuración en el Código

La aplicación ya está configurada para leer la API Key desde el archivo `.env` en la raíz del proyecto.

1.  Abre el archivo `.env` en la raíz del proyecto.
2.  Asegúrate de que existe la variable `GEOAPIFY_API_KEY` con tu clave:

```dotenv
GEOAPIFY_API_KEY=tu_api_key_aqui
```

No es necesario modificar los archivos HTML, ya que toman el valor automáticamente de esta variable de entorno.

## Notas Adicionales

*   Asegúrate de configurar las restricciones de seguridad (dominios permitidos) en el panel de Geoapify si vas a desplegar la aplicación en producción.
*   **APIs Requeridas**: Asegúrate de que la API Key tenga acceso a:
    *   **Address Autocomplete API**: Es la principal que usamos para el buscador de direcciones.
    *   **Geocoding API**: (Opcional pero recomendada) Para convertir direcciones en coordenadas si fuera necesario en el futuro.
