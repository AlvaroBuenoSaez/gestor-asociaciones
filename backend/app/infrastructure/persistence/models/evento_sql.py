from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.database import Base
import datetime

class EventoModel(Base):
    __tablename__ = "eventos_evento"

    id = Column(Integer, primary_key=True, index=True)
    asociacion_id = Column(Integer, ForeignKey("core_asociacionvecinal.id"), nullable=False)
    responsable_id = Column(Integer, ForeignKey("socias_socia.id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    lugar = Column(String(300), nullable=True)
    fecha = Column(DateTime, nullable=False)
    duracion = Column(BigInteger, nullable=True) # Stored as microseconds in Django SQLite
    colaboradores = Column(Text, nullable=True)
    evaluacion = Column(Integer, nullable=True)
    observaciones = Column(Text, nullable=True)

    asociacion = relationship("AsociacionVecinalModel")
    responsable = relationship("SociaModel")
