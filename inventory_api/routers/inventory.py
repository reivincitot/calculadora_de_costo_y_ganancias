from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, database
from auth_api.security import get_current_user, require_role


router = APIRouter(prefix="/inventory", tags=["inventory"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/batches/",
    response_model=schemas.Batch,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo lote (sólo admin)",
)
def create_batch(
    batch_in: schemas.BatchCreate,
    db: Session = Depends(get_db),
    # Sólo los usuarios con rol "admin" podrán crear lotes:
    #user=Depends(require_role("admin")),
):
    try:
        return crud.create_batch(db, batch_in)
    except Exception as e:
        # Parámetros inválidos, error interno, etc.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/consume/{sku}",
    summary="Consumir stock FIFO (cualquier usuario autenticado)",
)
def consume(
    sku: str,
    quantity: int,
    db: Session = Depends(get_db),
    # Cualquier usuario autenticado (admin u operador)
    #user=Depends(get_current_user),
):
    try:
        total_cost = crud.consume_stock(db, sku, quantity)
        return {
            "sku": sku,
            "quantity": quantity,
            "total_cost": total_cost,
        }
    except ValueError as ve:
        # No hay suficiente stock
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )


@router.get(
    "/stock/{sku}",
    summary="Leer stock total de un SKU",
)
def read_stock(
    sku: str,
    db: Session = Depends(get_db),
    #user=Depends(get_current_user),
):
    stock = crud.get_stock(db, sku)
    return {"sku": sku, "stock": stock}


@router.get(
    "/stock_value/{sku}",
    summary="Leer valor total del stock de un SKU",
)
def read_stock_value(
    sku: str,
    db: Session = Depends(get_db),
    #=Depends(get_current_user),
):
    val = crud.get_stock_value(db, sku)
    return {"sku": sku, "stock_value": val}


@router.post("/batches/", response_model=schemas.Batch)
def create_batch(
    batch_in: schemas.BatchCreate,
    db: Session = Depends(get_db),
    #user=Depends(require_role("admin"))
):
    return crud.create_batch(db, batch_in)
