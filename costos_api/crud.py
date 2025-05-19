from sqlalchemy.orm import Session
from . import models, schemas
from decimal import Decimal

def create_costo(db: Session, costo_in: schemas.CostoCreate) -> models.Costos:
    """Crea un nuevo registro en la tabla 'costos'."""
    db_item = models.Costos(**costo_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_costo_por_sku(db: Session, sku: str) -> list[models.Costos]:
    """Devuelve todos los registros de 'costos' para un SKU dado."""
    return db.query(models.Costos).filter(models.Costos.sku == sku).all()

def calcular_precio_sugerido(db: Session, sku: str) -> Decimal:
    """
    Suma todos los montos de costos para el SKU y aplica un margen del 30%.
    Devuelve el precio sugerido redondeado a 2 decimales.
    """
    costos = get_costo_por_sku(db, sku)
    total = sum(c.monto for c in costos) if costos else Decimal(0)
    return (total * Decimal("1.30")).quantize(Decimal("0.01"))