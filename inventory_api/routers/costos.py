# inventory_api/routers/costos.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/costos", tags=["costos"])


@router.get("/precio-sugerido/{sku}", response_model=schemas.PrecioSugeridoOut)
async def precio_sugerido(sku: str, db: Session = Depends(get_db)):
    try:
        return crud.get_precio_sugerido(db, sku)
    except KeyError:
        raise HTTPException(status_code=404, detail="SKU no encontrado")
