import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.api.deps import ensure_household_member, get_current_user
from app.db.session import get_db
from app.models.models import Budget, Category, HouseholdMember, Transaction, User
from app.schemas.budgeting import BudgetIn, TransactionIn, CategoryIn

router = APIRouter(prefix="", tags=["budgeting"])


def _hh(household_id: str):
    return uuid.UUID(household_id)


@router.get("/households/{household_id}/categories")
def list_categories(household_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    categories = db.scalars(select(Category).where(Category.household_id == hid)).all()
    return categories


@router.post("/households/{household_id}/categories")
def create_category(household_id: str, payload: CategoryIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = Category(household_id=hid, name=payload.name, color=payload.color)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/households/{household_id}/categories/{category_id}")
def update_category(household_id: str, category_id: str, payload: CategoryIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = db.get(Category, uuid.UUID(category_id))
    if not row or row.household_id != hid:
        raise HTTPException(status_code=404, detail="Not found")
    row.name, row.color = payload.name, payload.color
    db.commit()
    return row


@router.delete("/households/{household_id}/categories/{category_id}")
def delete_category(household_id: str, category_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = db.get(Category, uuid.UUID(category_id))
    if not row or row.household_id != hid:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return {"message": "deleted"}


@router.get("/households/{household_id}/budgets")
def list_budgets(household_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    return db.scalars(select(Budget).where(Budget.household_id == hid)).all()


@router.post("/households/{household_id}/budgets")
def create_budget(household_id: str, payload: BudgetIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = Budget(household_id=hid, category_id=uuid.UUID(payload.category_id), month=payload.month, amount=payload.amount)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/households/{household_id}/budgets/{budget_id}")
def update_budget(household_id: str, budget_id: str, payload: BudgetIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = db.get(Budget, uuid.UUID(budget_id))
    if not row or row.household_id != hid:
        raise HTTPException(status_code=404, detail="Not found")
    row.category_id, row.month, row.amount = uuid.UUID(payload.category_id), payload.month, payload.amount
    db.commit()
    return row


@router.delete("/households/{household_id}/budgets/{budget_id}")
def delete_budget(household_id: str, budget_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = db.get(Budget, uuid.UUID(budget_id))
    if not row or row.household_id != hid:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return {"message": "deleted"}


@router.get("/households/{household_id}/transactions")
def list_transactions(household_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    return db.scalars(select(Transaction).where(Transaction.household_id == hid)).all()


@router.post("/households/{household_id}/transactions")
def create_transaction(household_id: str, payload: TransactionIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = Transaction(
        household_id=hid,
        category_id=uuid.UUID(payload.category_id) if payload.category_id else None,
        description=payload.description,
        amount=payload.amount,
        occurred_on=payload.occurred_on,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/households/{household_id}/transactions/{transaction_id}")
def update_transaction(household_id: str, transaction_id: str, payload: TransactionIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = db.get(Transaction, uuid.UUID(transaction_id))
    if not row or row.household_id != hid:
        raise HTTPException(status_code=404, detail="Not found")
    row.category_id = uuid.UUID(payload.category_id) if payload.category_id else None
    row.description = payload.description
    row.amount = payload.amount
    row.occurred_on = payload.occurred_on
    db.commit()
    return row


@router.delete("/households/{household_id}/transactions/{transaction_id}")
def delete_transaction(household_id: str, transaction_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    row = db.get(Transaction, uuid.UUID(transaction_id))
    if not row or row.household_id != hid:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return {"message": "deleted"}


@router.get("/summary/monthly")
def monthly_summary(household_id: str, month: str = Query(..., pattern=r"^\d{4}-\d{2}$"), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hid = _hh(household_id)
    ensure_household_member(db, hid, user.id)
    target_month = date.fromisoformat(f"{month}-01")
    rows = db.execute(
        select(Category.name, func.coalesce(func.sum(Transaction.amount), 0))
        .select_from(Transaction)
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .where(
            Transaction.household_id == hid,
            func.date_trunc('month', Transaction.occurred_on) == func.date_trunc('month', target_month),
        )
        .group_by(Category.name)
    ).all()
    by_category = {name or "Uncategorized": float(total) for name, total in rows}
    total = sum(by_category.values())
    return {"month": month, "total_spent": total, "by_category": by_category}
