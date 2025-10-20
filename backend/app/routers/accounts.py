from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.entities import Account
from app.schemas.accounts import AccountCreate, AccountPublic

router = APIRouter()


@router.get("/", response_model=list[AccountPublic])
async def list_accounts(db: AsyncSession = Depends(get_db)) -> list[AccountPublic]:
    result = await db.execute(select(Account))
    return [AccountPublic.model_validate(row, from_attributes=True) for row in result.scalars().all()]


@router.post("/", response_model=AccountPublic, status_code=201)
async def create_account(payload: AccountCreate, db: AsyncSession = Depends(get_db)) -> AccountPublic:
    account = Account(
        user_id=payload.user_id,
        oanda_account_id=payload.oanda_account_id,
        env=payload.env,
        label=payload.label,
        is_default=payload.is_default,
        is_active=True,
    )
    db.add(account)
    await db.flush()
    await db.commit()
    await db.refresh(account)
    return AccountPublic.model_validate(account, from_attributes=True)
