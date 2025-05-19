from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from shared.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    """Crea todas las tablas declaradas bajo Base.metadata."""
    Base.metadata.create_all(bind=engine)

def close_db():
    """Libera el Engine (pool) al apagar la aplicación."""
    engine.dispose()

def get_db():
    """
    Dependency de FastAPI para obtener una sesión de DB por request.
    Usage:
        @router.get(...)
        def endpoint(..., db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
