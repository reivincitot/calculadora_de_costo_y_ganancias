from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, database


router = APIRouter(prefix="/costos", tags=["costos"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/", response_model=schemas.CostoRead)
def crear_costo(costo: schemas.CostoCreate, db: Session = Depends(get_db)):
    return crud.create_costo(db, costo)

@router.get("/{sku}", response_model=list[schemas.CostoRead])
def leer_costos(sku: str, db: Session = Depends(get_db)):
    return crud.get_costo_por_sku(db, sku)

@router.get("/precio-sugerido/{sku}", response_model=schemas.PrecioSugerido)
def precio_sugerido(sku: str, db: Session = Depends(get_db)):
    precio = crud.calcular_precio_sugerido(db, sku)
    return schemas.PrecioSugerido(sku=sku, precio_sugerido=precio)
