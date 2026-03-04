from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Budget, BudgetAlertState, DeviceToken, HouseholdMember, Transaction
from app.services.notifications import send_notification


def evaluate_budget_thresholds(db: Session, household_id):
    budgets = db.scalars(select(Budget).where(Budget.household_id == household_id)).all()
    member_ids = db.scalars(select(HouseholdMember.user_id).where(HouseholdMember.household_id == household_id)).all()
    tokens = db.scalars(select(DeviceToken.token).where(DeviceToken.user_id.in_(member_ids))).all() if member_ids else []

    for budget in budgets:
        spent = db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.household_id == household_id,
                Transaction.category_id == budget.category_id,
                func.date_trunc('month', Transaction.occurred_on) == func.date_trunc('month', budget.month),
            )
        ) or 0
        pct = float(spent) / float(budget.amount) if float(budget.amount) else 0
        state = db.scalar(select(BudgetAlertState).where(BudgetAlertState.budget_id == budget.id))
        if not state:
            state = BudgetAlertState(budget_id=budget.id)
            db.add(state)

        if pct >= 1 and not state.threshold_100_sent:
            send_notification(tokens, "Budget exceeded", f"Category budget exceeded for {budget.month}")
            state.threshold_100_sent = True
            state.last_notified_at = datetime.utcnow()
        elif pct >= 0.8 and not state.threshold_80_sent:
            send_notification(tokens, "Budget at 80%", f"Category budget reached 80% for {budget.month}")
            state.threshold_80_sent = True
            state.last_notified_at = datetime.utcnow()
