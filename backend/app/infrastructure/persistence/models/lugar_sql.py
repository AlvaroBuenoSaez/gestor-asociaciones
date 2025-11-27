from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.database import Base

class LugarModel(Base):
    __tablename__ = "lugares"

    id = Column(Integer, primary_key=True, index=True)
    asociacion_id = Column(Integer, ForeignKey("core_asociacionvecinal.id"), nullable=False)
    nombre = Column(String, index=True)
    direccion = Column(String, nullable=True)

    asociacion = relationship("AsociacionVecinalModel")
