from sqlalchemy import Column, Integer, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.sql import func
from .database import Base


class Costo(Base):
    __tablename__ = "costos"
    __table_args__ = (
        CheckConstraint("monto >=0", name="ck_costos_monto_nonnegative"),
    )
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), nullable=False, index=True)
    concepto = Column(String(100), nullable=False)
    monto = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
