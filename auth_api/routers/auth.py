from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import crud, schemas, database, security

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(database.SessionLocal)):
    existing = crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(400, "Username already registered")
    return crud.create_user(db, user_in)


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), body: dict = Body(None), db: Session = Depends(database.SessionLocal)):
    if body is not None:
        username = body.get("username")
        password = body.get("password")
    else:
        username = form_data.username
        password = form_data.password

    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = security.create_access_token(
        {"sub": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}
