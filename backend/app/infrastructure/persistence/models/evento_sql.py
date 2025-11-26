from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.database import Base
import datetime
from app.infrastructure.persistence.models.proyecto_sql import ProyectoModel  # Importar para registrar tabla

class EventoModel(Base):
    __tablename__ = "eventos_evento"

    id = Column(Integer, primary_key=True, index=True)
    asociacion_id = Column(Integer, ForeignKey("core_asociacionvecinal.id"), nullable=False)
    responsable_id = Column(Integer, ForeignKey("socias_socia.id"), nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos_proyecto.id"), nullable=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    lugar_nombre = Column(String(300), nullable=True)
    lugar_direccion = Column(String(500), nullable=True)
    fecha = Column(DateTime, nullable=False)
    duracion = Column(BigInteger, nullable=True) # Stored as microseconds in Django SQLite
    colaboradores = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    asociacion = relationship("AsociacionVecinalModel")
    responsable = relationship("SociaModel")
