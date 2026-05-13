from fastapi import FastAPI
from app.models.session import Session
from app.core.database import engine
from app.models.user import User
from app.core.database import Base
from app.routes.auth import router as auth_router

Base.metadata.create_all(bind = engine)
app = FastAPI(
    title="AuthFlowX",
    version="1.0.0"
)


app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message": "AuthFlowX Backend Running Successfully"
    }