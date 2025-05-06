from pydantic import BaseModel, Field
from datetime import datetime

class Producto(BaseModel):
    sku: str
    nombre: str
    costo_unitario: float
    fecha_creacion: datetime = Field(default_factory=datetime.now)
