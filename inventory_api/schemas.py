from pydantic import BaseModel, conint, confloat, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class Movement(BaseModel):
    id: int
    batch_id: int
    movement_type: str
    quantity: int
    unit_cost: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PrecioSugeridoOut(BaseModel):
    sku: str
    precio_sugerido: float

    model_config = ConfigDict(from_attributes=True)
