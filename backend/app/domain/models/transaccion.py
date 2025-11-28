from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class TipoTransaccion(str, Enum):
    ingreso = 'ingreso'
    gasto = 'gasto'

class TransaccionBase(BaseModel):
    cantidad: float
    concepto: str
    descripcion: Optional[str] = None
    fecha_transaccion: date
    fecha_vencimiento: Optional[date] = None
    entidad: Optional[str] = None
    
    # Foreign Keys
    evento_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    socia_id: Optional[int] = None
    
    # Drive
    drive_file_id: Optional[str] = None
    drive_file_link: Optional[str] = None
    drive_file_name: Optional[str] = None

class TransaccionCreate(TransaccionBase):
    asociacion_id: int

class TransaccionUpdate(BaseModel):
    cantidad: Optional[float] = None
    concepto: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_transaccion: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    entidad: Optional[str] = None
    evento_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    socia_id: Optional[int] = None
    drive_file_id: Optional[str] = None
    drive_file_link: Optional[str] = None
    drive_file_name: Optional[str] = None

class Transaccion(TransaccionBase):
    id: int
    asociacion_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
