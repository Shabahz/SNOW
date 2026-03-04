from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import PlaidConnection, Transaction
from app.services.budgets import evaluate_budget_thresholds
from app.services.crypto import decrypt_value


def create_link_token(user_id: str, household_id: str) -> str:
    if not settings.plaid_client_id:
        return "sandbox-link-token-placeholder"
    # Real Plaid link token call can be implemented here with plaid-python client.
    return "plaid-link-token-todo"


def sync_transactions_for_connection(db: Session, connection: PlaidConnection) -> dict[str, Any]:
    access_token = decrypt_value(connection.access_token_encrypted)
    if access_token.startswith("sandbox") or not settings.plaid_client_id:
        added = [
            {
                "transaction_id": "demo_txn_1",
                "name": "Sandbox Grocery",
                "amount": 42.50,
                "date": str(date.today()),
                "pending": False,
            }
        ]
        next_cursor = "demo-cursor-1"
    else:
        # Replace with transactions/sync request against Plaid client.
        added = []
        next_cursor = connection.sync_cursor

    for tx in added:
        existing = db.scalar(select(Transaction).where(Transaction.plaid_transaction_id == tx["transaction_id"]))
        if existing:
            existing.description = tx["name"]
            existing.amount = tx["amount"]
            existing.occurred_on = date.fromisoformat(tx["date"])
            existing.is_pending = tx.get("pending", False)
        else:
            db.add(
                Transaction(
                    household_id=connection.household_id,
                    plaid_connection_id=connection.id,
                    plaid_transaction_id=tx["transaction_id"],
                    description=tx["name"],
                    amount=tx["amount"],
                    occurred_on=date.fromisoformat(tx["date"]),
                    is_pending=tx.get("pending", False),
                )
            )

    connection.sync_cursor = next_cursor
    evaluate_budget_thresholds(db, connection.household_id)
    return {"added": len(added), "next_cursor": next_cursor}
