from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.database import Base
from datetime import datetime

class ProyectoModel(Base):
    __tablename__ = "proyectos_proyecto"

    id = Column(Integer, primary_key=True, index=True)
    asociacion_id = Column(Integer, ForeignKey("core_asociacionvecinal.id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    
    responsable_id = Column(Integer, ForeignKey("socias_socia.id"), nullable=True)
    
    involucrados = Column(Text, nullable=True)
    descripcion = Column(Text, nullable=True)
    materiales = Column(Text, nullable=True)
    lugar = Column(String(300), nullable=True)
    
    lugar_fk_id = Column(Integer, ForeignKey("lugares.id"), nullable=True)
    
    fecha_inicio = Column(Date, nullable=False)
    fecha_final = Column(Date, nullable=True)
    recursivo = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asociacion = relationship("AsociacionVecinalModel")
