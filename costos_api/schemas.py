from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class CostoCreate(BaseModel):
    sku: str = Field(..., example="SKU-123")
    concepto: str = Field(..., example="Materia Prima")
    monto: Decimal = Field(..., ge=0)
    

class CostoRead(CostoCreate):
    id: int
    created_at: datetime
    
    model_config ={"from_attributes": True}
    

class PrecioSugerido(BaseModel):
    sku: str
    precio_sugerido: Decimal

    model_config = {"json_schema_extra": {"example": {"sku": "SKU-123", "precio_sugerido": 123.45}}}