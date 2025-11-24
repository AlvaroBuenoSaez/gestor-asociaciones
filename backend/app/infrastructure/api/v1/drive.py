from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.models.user_sql import AsociacionVecinalModel
from app.infrastructure.external_services.google_drive_service import GoogleDriveService

router = APIRouter(
    prefix="/drive",
    tags=["drive"]
)

# Initialize service (will warn if credentials missing but won't crash app startup)
drive_service = GoogleDriveService()

class DriveConfig(BaseModel):
    asociacion_id: int
    folder_id: str

class AuthCallback(BaseModel):
    code: str
    asociacion_id: int

class CreateFolderRequest(BaseModel):
    asociacion_id: int
    folder_name: str

@router.get("/auth/url")
def get_auth_url():
    try:
        return {"url": drive_service.get_auth_url()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/callback")
def auth_callback(data: AuthCallback, db: Session = Depends(get_db)):
    try:
        credentials_json = drive_service.exchange_code(data.code)

        asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == data.asociacion_id).first()
        if not asociacion:
            raise HTTPException(status_code=404, detail="Asociación no encontrada")

        asociacion.drive_credentials = credentials_json
        db.commit()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/folders")
def list_folders(asociacion_id: int, parent_id: Optional[str] = None, db: Session = Depends(get_db)):
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == asociacion_id).first()
    if not asociacion or not asociacion.drive_credentials:
        raise HTTPException(status_code=400, detail="Drive no conectado")

    try:
        return drive_service.list_folders(asociacion.drive_credentials, parent_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
def configure_drive(config: DriveConfig, db: Session = Depends(get_db)):
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == config.asociacion_id).first()
    if not asociacion:
        raise HTTPException(status_code=404, detail="Asociación no encontrada")

    asociacion.drive_folder_id = config.folder_id
    db.commit()
    return {"status": "success", "folder_id": config.folder_id}

@router.get("/config/{asociacion_id}")
def get_drive_config(asociacion_id: int, db: Session = Depends(get_db)):
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == asociacion_id).first()
    if not asociacion:
        raise HTTPException(status_code=404, detail="Asociación no encontrada")

    folder_metadata = {}
    if asociacion.drive_folder_id and asociacion.drive_credentials:
        folder_metadata = drive_service.get_file_metadata(asociacion.drive_credentials, asociacion.drive_folder_id)

    return {
        "drive_folder_id": asociacion.drive_folder_id,
        "is_connected": bool(asociacion.drive_credentials),
        "folder_name": folder_metadata.get('name'),
        "folder_link": folder_metadata.get('webViewLink')
    }

@router.get("/files")
def list_files(asociacion_id: int, db: Session = Depends(get_db)):
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == asociacion_id).first()
    if not asociacion:
        raise HTTPException(status_code=404, detail="Asociación no encontrada")

    if not asociacion.drive_folder_id or not asociacion.drive_credentials:
        raise HTTPException(status_code=400, detail="Drive no configurado")

    try:
        return drive_service.list_files_in_folder(asociacion.drive_credentials, asociacion.drive_folder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(
    asociacion_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == asociacion_id).first()
    if not asociacion:
        raise HTTPException(status_code=404, detail="Asociación no encontrada")

    if not asociacion.drive_folder_id or not asociacion.drive_credentials:
        raise HTTPException(status_code=400, detail="Drive no configurado")

    try:
        return drive_service.upload_file(asociacion.drive_credentials, file, asociacion.drive_folder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{file_id}")
def delete_file(file_id: str, asociacion_id: int, db: Session = Depends(get_db)):
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == asociacion_id).first()
    if not asociacion or not asociacion.drive_credentials:
        raise HTTPException(status_code=400, detail="Drive no configurado")

    try:
        drive_service.delete_file(asociacion.drive_credentials, file_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-folder")
def create_folder(data: CreateFolderRequest, db: Session = Depends(get_db)):
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == data.asociacion_id).first()
    if not asociacion or not asociacion.drive_credentials:
        raise HTTPException(status_code=400, detail="Drive no conectado")

    try:
        folder = drive_service.create_folder(asociacion.drive_credentials, data.folder_name)

        # Auto-configure as base folder
        asociacion.drive_folder_id = folder['id']
        db.commit()

        return {"status": "success", "folder": folder}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-transaction-file")
async def upload_transaction_file(
    asociacion_id: int = Form(...),
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print(f"DEBUG: Upload request received. Asoc: {asociacion_id}, Trans: {transaction_id}, File: {file.filename}")
    asociacion = db.query(AsociacionVecinalModel).filter(AsociacionVecinalModel.id == asociacion_id).first()
    if not asociacion:
        print("DEBUG: Asociacion not found")
        raise HTTPException(status_code=404, detail="Asociación no encontrada")

    if not asociacion.drive_folder_id or not asociacion.drive_credentials:
        print("DEBUG: Drive not configured")
        raise HTTPException(status_code=400, detail="Drive no configurado")

    try:
        # Ensure folder structure: Transacciones / {transaction_id}
        folder_path = ['Transacciones', str(transaction_id)]
        print(f"DEBUG: Ensuring folder path: {folder_path} in root {asociacion.drive_folder_id}")

        target_folder_id = drive_service.ensure_folder_path(
            asociacion.drive_credentials,
            folder_path,
            asociacion.drive_folder_id
        )
        print(f"DEBUG: Target folder ID: {target_folder_id}")

        # Upload file
        print(f"DEBUG: Uploading file {file.filename}...")
        uploaded_file = drive_service.upload_file(asociacion.drive_credentials, file, target_folder_id)
        print(f"DEBUG: File uploaded: {uploaded_file}")
        return uploaded_file
    except Exception as e:
        print(f"DEBUG: Error uploading file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
