from pydantic import BaseModel, Field, validator
import re

class BatchValidator(BaseModel):
    sku: str = Field(..., min_length=5, max_length=20)
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)
    document: str | None = Field(None, max_length=20)

    @validator('sku')
    def validate_sku_format(cls, v):
        if not re.match(r'^[A-Z0-9-]+$', v):
            raise ValueError('Formato SKU inválido. Solo mayúsculas, números y guiones')
        return v

class ConsumeValidator(BaseModel):
    sku: str = Field(..., min_length=5, max_length=20)
    quantity: int = Field(..., gt=0)
    user: str = Field(..., min_length=3)
    document: str = Field(..., min_length=3)