from fastapi import FastAPI
from .database import init_db
from .routers import costos


app = FastAPI(title="Costos API", version="0.1.0")
app.include_router(costos.router)


@app.on_event("startup")
def on_startup():
    init_db()  