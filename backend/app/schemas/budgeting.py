from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class CategoryIn(BaseModel):
    name: str
    color: str | None = None


class CategoryOut(CategoryIn):
    id: str


class BudgetIn(BaseModel):
    category_id: str
    month: date
    amount: Decimal


class BudgetOut(BudgetIn):
    id: str


class TransactionIn(BaseModel):
    category_id: str | None = None
    description: str
    amount: Decimal
    occurred_on: date


class TransactionOut(TransactionIn):
    id: str
