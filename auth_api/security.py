import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import crud, schemas, database
from shared.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.SessionLocal),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if not username or not role:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, role=role)

    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, token_data.username)
    if user is None or not getattr(user, "is_active", True):
        raise credentials_exception
    return user


def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return role_checker
