from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import DeclarativeBase

from app.api import auth, budgeting, households, plaid
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(auth.router)
app.include_router(households.router)
app.include_router(budgeting.router)
app.include_router(plaid.router)


@app.get("/health")
def health():
    return {"status": "ok"}
