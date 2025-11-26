from sqlalchemy import Column, Integer, String
from app.infrastructure.persistence.database import Base

class LugarModel(Base):
    __tablename__ = "lugares"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    direccion = Column(String)
