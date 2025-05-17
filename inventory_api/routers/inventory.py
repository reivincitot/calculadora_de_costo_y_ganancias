from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(prefix="/inventory", tags=["inventory"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/batches/", response_model=schemas.Batch)
def create_batch(batch_in: schemas.BatchCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_batch(db, batch_in)
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/consume/{sku}")
def consume(sku: str, quantity: int, db: Session = Depends(get_db)):
    try:
        cost = crud.consume_stock(db, sku, quantity)
        return {"sku": sku, "quantity": quantity, "total_cost": cost}
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/stock/{sku}")
def read_stock(sku: str, db: Session = Depends(get_db)):
    return {"sku": sku, "stock": crud.get_stock(db, sku)}

@router.get("/stock_value/{sku}")
def read_stock_value(sku: str, db: Session = Depends(get_db)):
    return {"sku": sku, "stock_value": crud.get_stock_value(db, sku)}
