from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.database import Base
import datetime

class SociaModel(Base):
    __tablename__ = "socias_socia"

    id = Column(Integer, primary_key=True, index=True)
    asociacion_id = Column(Integer, ForeignKey("core_asociacionvecinal.id"), nullable=False)
    numero_socia = Column(String(20), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    provincia = Column(String(100), nullable=True)
    codigo_postal = Column(String(10), nullable=True)
    pais = Column(String(100), default='España')
    nacimiento = Column(Date, nullable=True)
    fecha_inscripcion = Column(Date, default=datetime.date.today)
    pagado = Column(Boolean, default=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    asociacion = relationship("AsociacionVecinalModel")
