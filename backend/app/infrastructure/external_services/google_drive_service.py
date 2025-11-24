import os
import io
import json
from typing import List, Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fastapi import UploadFile

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveService:
    def __init__(self, client_secrets_path: str = "client_secrets.json"):
        # Allow OAuth over HTTP for localhost
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        # Check if file exists, if not try backend/ prefix (common issue when running from root)
        if not os.path.exists(client_secrets_path) and os.path.exists(f"backend/{client_secrets_path}"):
            client_secrets_path = f"backend/{client_secrets_path}"

        self.client_secrets_path = client_secrets_path
        # Redirect to the Django frontend callback view
        self.redirect_uri = "http://localhost:8000/users/dashboard/drive/callback/"

    def get_auth_url(self) -> str:
        if not os.path.exists(self.client_secrets_path):
            raise Exception(f"Client secrets file not found at {self.client_secrets_path}")

        flow = Flow.from_client_secrets_file(
            self.client_secrets_path,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url

    def exchange_code(self, code: str) -> str:
        flow = Flow.from_client_secrets_file(
            self.client_secrets_path,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        return creds.to_json()

    def get_service(self, credentials_json: str):
        if not credentials_json:
            return None

        creds_dict = json.loads(credentials_json)
        creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
        return build('drive', 'v3', credentials=creds)

    def list_folders(self, credentials_json: str, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        service = self.get_service(credentials_json)
        if not service:
            return []

        query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, parents)"
        ).execute()

        return results.get('files', [])

    def upload_file(self, credentials_json: str, file: UploadFile, parent_id: str) -> Dict[str, Any]:
        service = self.get_service(credentials_json)
        if not service:
            raise Exception("Google Drive service not initialized")

        file_metadata = {
            'name': file.filename,
            'parents': [parent_id]
        }

        # Read file content into memory
        content = file.file.read()
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type, resumable=True)

        file_drive = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        return file_drive

    def delete_file(self, credentials_json: str, file_id: str):
        service = self.get_service(credentials_json)
        if not service:
            raise Exception("Google Drive service not initialized")

        service.files().delete(fileId=file_id).execute()

    def list_files_in_folder(self, credentials_json: str, folder_id: str) -> List[Dict[str, Any]]:
        service = self.get_service(credentials_json)
        if not service:
            return []

        query = f"'{folder_id}' in parents and trashed = false"

        results = service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, webViewLink, iconLink, createdTime)"
        ).execute()

        return results.get('files', [])

    def create_folder(self, credentials_json: str, folder_name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        service = self.get_service(credentials_json)
        if not service:
            raise Exception("Google Drive service not initialized")

        file_metadata: Dict[str, Any] = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_id:
            file_metadata['parents'] = [parent_id]

        file = service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()

        return file

    def get_file_metadata(self, credentials_json: str, file_id: str) -> Dict[str, Any]:
        service = self.get_service(credentials_json)
        if not service:
            return {}

        try:
            file = service.files().get(fileId=file_id, fields='id, name, webViewLink, mimeType').execute()
            return file
        except Exception:
            return {}

    def ensure_folder_path(self, credentials_json: str, path_parts: List[str], root_id: str) -> str:
        """
        Ensures a folder path exists starting from root_id.
        Returns the ID of the final folder.
        """
        print(f"DEBUG: ensure_folder_path called with root_id={root_id}, parts={path_parts}")
        service = self.get_service(credentials_json)
        if not service:
            raise Exception("Google Drive service not initialized")

        current_parent_id = root_id

        for folder_name in path_parts:
            # Check if folder exists in current parent
            query = f"mimeType = 'application/vnd.google-apps.folder' and '{current_parent_id}' in parents and name = '{folder_name}' and trashed = false"
            print(f"DEBUG: Searching folder with query: {query}")
            results = service.files().list(q=query, fields="files(id)").execute()
            files = results.get('files', [])

            if files:
                # Folder exists, use it
                current_parent_id = files[0]['id']
                print(f"DEBUG: Found existing folder '{folder_name}' with ID {current_parent_id}")
            else:
                # Create folder
                print(f"DEBUG: Creating folder '{folder_name}' in parent {current_parent_id}")
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [current_parent_id]
                }
                folder = service.files().create(body=file_metadata, fields='id').execute()
                current_parent_id = folder['id']
                print(f"DEBUG: Created folder '{folder_name}' with ID {current_parent_id}")

        return current_parent_id

