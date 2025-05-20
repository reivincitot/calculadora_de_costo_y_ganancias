import uvicorn
from fastapi import FastAPI
from .database import Base, engine
from .routers import auth

# Crea tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Microservice")
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run("auth_api.main:app", host="0.0.0.0", port=8002, reload=True)
