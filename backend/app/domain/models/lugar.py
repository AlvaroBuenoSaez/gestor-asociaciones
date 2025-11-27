from pydantic import BaseModel
from typing import Optional

class LugarBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None

class LugarCreate(LugarBase):
    asociacion_id: int

class Lugar(LugarBase):
    id: int
    asociacion_id: int

    class Config:
        from_attributes = True
