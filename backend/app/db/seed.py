from __future__ import annotations

import asyncio

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionMaker
from app.models.entities import Strategy, User
from app.utils.security import get_password_hash


async def seed() -> None:
    async with AsyncSessionMaker() as session:  # type: AsyncSession
        await seed_user(session)
        await seed_strategy(session)
        await session.commit()


async def seed_user(session: AsyncSession) -> None:
    exists = await session.execute(
        sa.select(User).where(User.email == "admin@local.test")  # type: ignore[name-defined]
    )
    if exists.scalar_one_or_none():
        return
    user = User(email="admin@local.test", password_hash=get_password_hash("ChangeMe123!"), role="admin")
    session.add(user)


async def seed_strategy(session: AsyncSession) -> None:
    exists = await session.execute(
        sa.select(Strategy).where(Strategy.name == "HullSuite")  # type: ignore[name-defined]
    )
    if exists.scalar_one_or_none():
        return
    strategy = Strategy(name="HullSuite", code="hullsuite", params_json={"timeframe": "15m"})
    session.add(strategy)


if __name__ == "__main__":
    asyncio.run(seed())
