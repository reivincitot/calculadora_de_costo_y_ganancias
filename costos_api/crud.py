from sqlalchemy.orm import Session
from . import models, schemas
from decimal import Decimal


def create_costo(db: Session, costo_in: schemas.CostoCreate) ->models.Costo:
    db_item = models.Costo(**costo_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_costo_por_sku(db: Session, sku: str):
    return db.query(models.Costo).filter(models.Costo.sku == sku).all()

def calcular_precio_sugerido(db: Session, sku: str) -> Decimal:
    # ejemplo sumar todos los costos y aplicar margen del 30%
    costos = get_costo_por_sku(db, sku)
    total = sum(c.monto for c in costos) if costos else Decimal(0)
    return (total * Decimal("1.30")).quantize(Decimal("0.01"))
