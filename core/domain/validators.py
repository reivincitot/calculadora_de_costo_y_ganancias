from pydantic import BaseModel, Field, field_validator
import re

class BatchCreateSchema(BaseModel):
    sku: str = Field(..., min_length=5, max_length=20)
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)
    document: str | None = Field(None, max_length=20)

    @field_validator('sku')
    def validate_sku_format(cls, v):
        if not re.match(r'^[A-Z0-9-]{5,20}$', v):
            raise ValueError('Formato SKU inválido. Solo mayúsculas, números y guiones (5-20 caracteres)')
        return v

    @field_validator('unit_cost')
    def validate_cost(cls, v):
        if v > 100_000_000:
            raise ValueError('Costo unitario excede máximo permitido (100,000,000 CLP)')
        return round(v, 2)

class ConsumeValidator(BaseModel):
    sku: str = Field(..., min_length=5, max_length=20)
    quantity: int = Field(..., gt=0)
    user: str = Field(..., min_length=3)
    document: str = Field(..., min_length=3)

    @field_validator('document')
    def validate_document_format(cls, v):
        if not re.match(r'^[A-Z]{3}-\d{4}$', v):
            raise ValueError('Formato documento inválido. Use AAA-0000')
        return v
