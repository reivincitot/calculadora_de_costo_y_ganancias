import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import init_db, close_db
from .routers import costos


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    close_db()


app = FastAPI(
    title="Costos API",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(costos.router)

if __name__ == "__main__":
    uvicorn.run(
        "costos_api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
