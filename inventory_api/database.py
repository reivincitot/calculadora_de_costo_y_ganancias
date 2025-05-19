from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from shared.config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Fixture de dependencia para FastAPI.
    Abre una sesión, la cede, y se asegura de cerrarla al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
