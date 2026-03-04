from datetime import date
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Message(BaseModel):
    message: str


class MonthlySummary(BaseModel):
    month: str
    total_spent: float
    by_category: dict[str, float]
