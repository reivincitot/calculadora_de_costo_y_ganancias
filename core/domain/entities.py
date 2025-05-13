from pydantic import BaseModel, SecretStr


class Usuario(BaseModel):
    id: int
    rut: str
    nombre: str
    rol: str
    hashed_password: str
    activo: bool = True

    