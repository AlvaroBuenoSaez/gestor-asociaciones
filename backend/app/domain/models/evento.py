from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

class EventoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    lugar: Optional[str] = None
    fecha: datetime
    duracion: Optional[timedelta] = None
    colaboradores: Optional[str] = None
    evaluacion: Optional[int] = Field(None, ge=1, le=5)
    observaciones: Optional[str] = None

class EventoCreate(EventoBase):
    asociacion_id: int
    responsable_id: int

class EventoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    lugar: Optional[str] = None
    fecha: Optional[datetime] = None
    duracion: Optional[timedelta] = None
    colaboradores: Optional[str] = None
    evaluacion: Optional[int] = Field(None, ge=1, le=5)
    observaciones: Optional[str] = None
    responsable_id: Optional[int] = None

class Evento(EventoBase):
    id: int
    asociacion_id: int
    responsable_id: int

    class Config:
        from_attributes = True
