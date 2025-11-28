from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Numeric
from sqlalchemy.orm import relationship
from app.infrastructure.persistence.database import Base
import datetime

class TransaccionModel(Base):
    __tablename__ = "finanzas_transaccion"

    id = Column(Integer, primary_key=True, index=True)
    asociacion_id = Column(Integer, ForeignKey("core_asociacionvecinal.id"), nullable=False)
    
    cantidad = Column(Numeric(10, 2), nullable=False)
    concepto = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    fecha_transaccion = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    
    evento_id = Column(Integer, ForeignKey("eventos_evento.id"), nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos_proyecto.id"), nullable=True)
    socia_id = Column(Integer, ForeignKey("socias_socia.id"), nullable=True)
    entidad = Column(String(200), nullable=True)
    
    drive_file_id = Column(String(100), nullable=True)
    drive_file_link = Column(String(200), nullable=True)
    drive_file_name = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
