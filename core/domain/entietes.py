from pydantic import BaseModel
from datetime import datetime

class Producto(BaseModel):
    sku: str
    nombre: str
    costo_unitario: float
    fecha_creacion: datetime = datetime.now()