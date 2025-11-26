from pydantic import BaseModel
from typing import Optional

class LugarBase(BaseModel):
    nombre: str
    direccion: str

class Lugar(LugarBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True
