from .database import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint


class Batch(Base):
    __tablename__ = "batches"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_batches_quantity_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Movement(Base):
    __tablename__ = "movements"
    __table_args__ = (
        CheckConstraint("movement_type IN ('IN', 'OUT')", name="ck_movements_type_valid"),
    )

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(3), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Costos(Base):
    __tablename__ = "costos"
    __table_args__ = (
        CheckConstraint("monto >= 0", name="ck_costos_monto_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), nullable=False, index=True)
    concepto = Column(String(100), nullable=False)
    monto = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
