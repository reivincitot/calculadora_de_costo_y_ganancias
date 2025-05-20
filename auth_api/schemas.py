from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    
    model_config = {"from_attributes": True}
    
    
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    
    model_config = {"from_attributes": True}
    
    
class TokenData(BaseModel):
    username: str
    role: str
    
    model_config = {"from_attributes": True}
    