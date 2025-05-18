import uvicorn
from fastapi import FastAPI
from .database import engine, Base
from .routers import inventory, costos

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Microservice")

app.include_router(inventory.router)
app.include_router(costos.router)

if __name__ == "__main__":
    uvicorn.run("inventory_api.main:app", host="0.0.0.0", port=8000, reload=True)
