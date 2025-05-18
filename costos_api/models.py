from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from .database import Base


class Costos(Base):
    __tablename__ = "costos"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), nullable=False, index=True)
    concepto = Column(String(100), nullable=False)
    monto = Column(
        Numeric(15,2), 
        CheckConstraint("monto >=0"), 
        nullable=False
        )
    created_at = Column(func.now(), nullable=False) 