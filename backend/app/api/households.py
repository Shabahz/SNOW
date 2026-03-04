import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Household, HouseholdMember, MemberRole, User
from app.schemas.household import HouseholdCreate, HouseholdJoin

router = APIRouter(prefix="/households", tags=["households"])


@router.post("")
def create_household(payload: HouseholdCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hh = Household(name=payload.name, invite_code=secrets.token_hex(4).upper())
    db.add(hh)
    db.flush()
    db.add(HouseholdMember(household_id=hh.id, user_id=user.id, role=MemberRole.owner))
    db.commit()
    return {"id": hh.id, "name": hh.name, "invite_code": hh.invite_code}


@router.post("/join")
def join_household(payload: HouseholdJoin, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hh = db.scalar(select(Household).where(Household.invite_code == payload.invite_code))
    if not hh:
        raise HTTPException(status_code=404, detail="Invite code not found")
    exists = db.scalar(select(HouseholdMember).where(HouseholdMember.household_id == hh.id, HouseholdMember.user_id == user.id))
    if not exists:
        db.add(HouseholdMember(household_id=hh.id, user_id=user.id, role=MemberRole.member))
        db.commit()
    return {"household_id": hh.id, "name": hh.name}
