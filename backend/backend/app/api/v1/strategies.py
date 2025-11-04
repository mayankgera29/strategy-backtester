from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.session import engine
from app.db.models import Strategy

router = APIRouter()
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: int) -> Dict[str, Any]:
    """
    Return a saved strategy by id.
    """
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(Strategy).where(Strategy.id == strategy_id))
        strategy = q.scalars().first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Try to safely extract graph and metadata
        result = {
            "id": strategy.id,
            "name": strategy.name,
            "graph": getattr(strategy, "graph", None),
            "metadata": getattr(strategy, "metadata", None),
        }
        return result
