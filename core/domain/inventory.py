from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re


class LoteSII(BaseModel):
    id: int
    sku: str = Field(..., pattern=r'CL-\d{4}-[A-Z]{3}$')
    cantidad: int = Field(..., gt=0)
    costo_unitario: float = Field(..., gt=0)
    fecha_ingreso: datetime = Field(default_factory=datetime.now)
    usuario: str = Field(..., min_length=3)
    documento_relacionado: str = Field(None, pattern=r'F-\d+$')

    @field_validator('sku')
    def validate_sku(cls, v):
        if not re.match(r'^CL-\d{4}-[A-Z]{3}$', v):
            raise ValueError('Formato SKU inválido. Debe ser CL-AAA-XXX')
        return v

class MovimientoInventario(BaseModel):
    tipo: str = Field(..., pattern='^(ENTRADA|SALIDA)$')
    cantidad: int
    costo_total: float
    fecha: datetime = Field(default_factory=datetime.now)
    referencias: str  # Número de documento tributario

