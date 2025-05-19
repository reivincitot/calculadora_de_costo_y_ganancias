from sqlalchemy.orm import Session
from . import models, schemas
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException


def create_costo(db: Session, costo_in: schemas.CostoCreate) -> models.Costo:
    """Crea un nuevo registro en la tabla 'costos'."""
    db_item = models.Costo(**costo_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_costo_por_sku(db: Session, sku: str) -> list[models.Costo]:
    """Devuelve todos los registros de 'costos' para un SKU dado."""
    return db.query(models.Costo).filter(models.Costo.sku == sku).all()


def calcular_precio_sugerido(db: Session, sku: str) -> schemas.PrecioSugeridoOut:
    """
    Suma todos los montos de costos para el SKU y aplica un margen del 30%.
    Devuelve el precio sugerido redondeado a 2 decimales.
    """
    costos = get_costo_por_sku(db, sku)
    if not costos:
        raise HTTPException(status_code=404, detail=f"SKU {sku} no encontrado")
    total = sum(c.monto for c in costos)
    precio = (total * Decimal('1.30')).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    return schemas.PrecioSugeridoOut(sku=sku, precio_sugerido=precio)
