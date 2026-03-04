import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import ensure_household_member, get_current_user
from app.db.session import get_db
from app.models.models import PlaidConnection, User
from app.schemas.plaid import ExchangePublicTokenRequest, LinkTokenRequest, PlaidWebhookPayload
from app.services.crypto import encrypt_value
from app.services.plaid_service import create_link_token, sync_transactions_for_connection

router = APIRouter(prefix="/plaid", tags=["plaid"])


@router.post("/link-token")
def link_token(payload: LinkTokenRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    household_id = uuid.UUID(payload.household_id)
    ensure_household_member(db, household_id, user.id)
    token = create_link_token(str(user.id), payload.household_id)
    return {"link_token": token}


@router.post("/exchange-public-token")
def exchange_public_token(payload: ExchangePublicTokenRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    household_id = uuid.UUID(payload.household_id)
    ensure_household_member(db, household_id, user.id)

    item_id = f"sandbox-item-{payload.public_token[-6:]}"
    access_token = f"sandbox-access-{payload.public_token[-8:]}"

    existing = db.scalar(select(PlaidConnection).where(PlaidConnection.item_id == item_id))
    if existing:
        raise HTTPException(status_code=409, detail="Connection already exists")
    conn = PlaidConnection(
        household_id=household_id,
        item_id=item_id,
        access_token_encrypted=encrypt_value(access_token),
        sync_cursor=None,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return {"connection_id": conn.id, "item_id": conn.item_id}


@router.post("/sync/{connection_id}")
def sync_connection(connection_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conn = db.get(PlaidConnection, uuid.UUID(connection_id))
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    ensure_household_member(db, conn.household_id, user.id)
    result = sync_transactions_for_connection(db, conn)
    db.commit()
    return result


@router.post("/webhook")
def plaid_webhook(payload: PlaidWebhookPayload, db: Session = Depends(get_db)):
    if payload.item_id:
        conn = db.scalar(select(PlaidConnection).where(PlaidConnection.item_id == payload.item_id))
        if conn and payload.webhook_code in {"SYNC_UPDATES_AVAILABLE", "DEFAULT_UPDATE"}:
            sync_transactions_for_connection(db, conn)
            db.commit()
    return {"status": "ok"}
