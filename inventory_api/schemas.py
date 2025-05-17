from pydantic import BaseModel, conint, confloat
from datetime import datetime

class BatchCreate(BaseModel):
    sku: str
    quantity: conint(gt=0)
    unit_cost: confloat(gt=0)

class Batch(BaseModel):
    id: int
    sku: str
    quantity: int
    unit_cost: float
    created_at: datetime

    class Config:
        orm_mode = True

class Movement(BaseModel):
    id: int
    batch_id: int
    movement_type: str
    quantity: int
    unit_cost: float
    created_at: datetime

    class Config:
        orm_mode = True
