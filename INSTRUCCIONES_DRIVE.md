# Instrucciones de Configuración de Google Drive (OAuth 2.0)

Para activar la funcionalidad de gestión de documentos con Google Drive de forma segura y sin usar claves de cuenta de servicio, utilizaremos OAuth 2.0.

## 1. Configuración en Google Cloud Console

1.  Accede a la [Google Cloud Console](https://console.cloud.google.com/).
2.  Crea un nuevo proyecto o selecciona uno existente.
3.  En el menú lateral, ve a **"APIs y servicios" > "Biblioteca"**.
4.  Busca **"Google Drive API"** y actívala.
5.  Ve a **"APIs y servicios" > "Pantalla de consentimiento de OAuth"**.
    *   Selecciona **"Externo"** (o Interno si tienes Google Workspace).
    *   Rellena los campos obligatorios (Nombre de la app, correos de soporte) y dale a "Guardar y Continuar".
    *   **Nota**: Si ya has pasado el asistente inicial y estás en el panel de control de la pantalla de consentimiento (donde ves pestañas como "Información de la marca", "Clientes", etc.), ve a la sección **"Acceso a los datos"** (Data Access).
    *   Haz clic en el botón **"Agregar o quitar permisos"**.
    *   En el filtro, escribe `drive` y busca la API **"Google Drive API"**.
    *   Selecciona la casilla que dice `.../auth/drive.file` (suele decir "Ver, editar, crear y borrar solo los archivos específicos de Google Drive que uses con esta aplicación").
    *   **NO** selecciones la que dice `.../auth/drive` (acceso completo), ya que es menos segura.
    *   Haz clic en "Actualizar" y luego en "Guardar".
    *   En la sección **"Usuarios de prueba"** (o "Público" > "Usuarios de prueba"), añade tu correo electrónico.
6.  Ve a **"APIs y servicios" > "Credenciales"**.
7.  Haz clic en **"Crear credenciales"** y selecciona **"ID de cliente de OAuth"**.
8.  Tipo de aplicación: **"Aplicación web"**.
9.  Nombre: `Gestor Asociaciones Web`.
10. En **"Orígenes autorizados de JavaScript"**, añade: `http://localhost:8000` (o tu dominio en producción).
11. En **"URI de redireccionamiento autorizados"**, añade: `http://localhost:8000/users/dashboard/drive/callback/`.
12. Haz clic en **"Crear"**.
13. Descarga el archivo JSON de credenciales.

## 2. Instalación de Credenciales en el Proyecto

1.  Localiza el archivo JSON descargado.
2.  Renómbralo a `client_secrets.json`.
3.  Copia este archivo en la carpeta `backend/` de tu proyecto.
    *   Ruta final: `/home/abueno/workspaces/alvarobueno/avl-propuesta/gestor-asociaciones/backend/client_secrets.json`

> **IMPORTANTE**: Asegúrate de que este archivo `client_secrets.json` esté incluido en tu `.gitignore`.

## 3. Conexión desde la Aplicación

1.  Inicia la aplicación.
2.  Ve al Dashboard -> **"📂 Documentos"** -> **"Configurar Carpeta"**.
3.  Verás un botón **"Conectar con Google"**. Haz clic en él.
4.  Se abrirá una ventana de Google para que inicies sesión y autorices a la aplicación.
5.  Una vez autorizado, volverás a la pantalla de configuración.
6.  Haz clic en el botón **"Crear Nueva Carpeta"**.
    *   Esto creará automáticamente una carpeta llamada "Gestor Asociaciones" en tu Drive.
    *   La aplicación solo tendrá acceso a los archivos dentro de esta carpeta.

¡Listo! La aplicación ahora actúa en tu nombre para gestionar los archivos de forma segura y restringida.
