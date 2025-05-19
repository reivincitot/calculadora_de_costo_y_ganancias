from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(prefix="/costos", tags=["costos"])

@router.post("/", response_model=schemas.CostoRead, status_code=status.HTTP_201_CREATED)
def crear_costo(
    costo: schemas.CostoCreate,
    db: Session = Depends(database.get_db)
):
    return crud.create_costo(db, costo)

@router.get("/{sku}", response_model=list[schemas.CostoRead])
def leer_costos(
    sku: str,
    db: Session = Depends(database.get_db)
):
    return crud.get_costo_por_sku(db, sku)

@router.get(
    "/precio-sugerido/{sku}",
    response_model=schemas.PrecioSugeridoOut
)
def precio_sugerido(
    sku: str,
    db: Session = Depends(database.get_db)
):
    try:
        return crud.calcular_precio_sugerido(db, sku)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
