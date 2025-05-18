from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func
from .models import Costos

def create_batch(db: Session, batch_in: schemas.BatchCreate) -> models.Batch:
    db_batch = models.Batch(**batch_in.model_dump())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    # registrar movimiento IN
    mov = models.Movement(
        batch_id=db_batch.id,
        movement_type="IN",
        quantity=db_batch.quantity,
        unit_cost=db_batch.unit_cost
    )
    db.add(mov)
    db.commit()
    return db_batch

def consume_stock(db: Session, sku: str, qty: int) -> float:
    # FIFO consumption
    batches = db.query(models.Batch).filter(
        models.Batch.sku == sku, models.Batch.quantity > 0
    ).order_by(models.Batch.created_at).all()
    remaining = qty
    total_cost = 0.0
    for b in batches:
        if remaining <= 0:
            break
        take = min(b.quantity, remaining)
        b.quantity -= take
        db.add(b)
        mov = models.Movement(
            batch_id=b.id,
            movement_type="OUT",
            quantity=take,
            unit_cost=b.unit_cost
        )
        db.add(mov)
        total_cost += float(take * b.unit_cost)
        remaining -= take
    if remaining > 0:
        raise ValueError(f"No hay suficiente stock para {qty} unidades de {sku}")
    db.commit()
    return total_cost

def get_stock(db: Session, sku: str) -> int:
    res = db.query(func.coalesce(func.sum(models.Batch.quantity), 0)).filter(
        models.Batch.sku == sku
    ).scalar()
    return int(res)

def get_stock_value(db: Session, sku: str) -> float:
    res = db.query(func.coalesce(func.sum(
        models.Batch.quantity * models.Batch.unit_cost
    ), 0.0)).filter(models.Batch.sku == sku).scalar()
    return float(res)

def get_precio_sugerido(db: Session, sku: str) -> schemas.PrecioSugeridoOut:
    costo = db.query(models.Costos).filter(models.Costos.sku == sku).first()
    if not costo:
        raise KeyError(f"Costo no encontrado para SKU {sku}")
    factor = 1.3  # ejemplo de margen del 30%
    precio = float(costo.monto) * factor
    return schemas.PrecioSugeridoOut(sku=sku, precio_sugerido=precio)
