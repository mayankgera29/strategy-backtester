from sqlalchemy import select, update
from app.db.models import Strategy, BacktestJob
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

# Strategy CRUD
async def create_strategy(db: AsyncSession, payload: Dict[str, Any]) -> Strategy:
    s = Strategy(name=payload.get("name"), graph=payload.get("graph"), meta=payload.get("metadata"))
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s

async def list_strategies(db: AsyncSession):
    q = select(Strategy).order_by(Strategy.created_at.desc())
    r = await db.execute(q)
    return r.scalars().all()

async def get_strategy(db: AsyncSession, strategy_id: int) -> Optional[Strategy]:
    q = select(Strategy).where(Strategy.id == strategy_id)
    r = await db.execute(q)
    return r.scalar_one_or_none()

# Backtest job CRUD
async def create_backtest_job(db: AsyncSession, payload: Dict[str, Any]) -> BacktestJob:
    job = BacktestJob(payload=payload, status="queued")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def fetch_next_queued_job(db: AsyncSession) -> Optional[BacktestJob]:
    q = select(BacktestJob).where(BacktestJob.status == "queued").order_by(BacktestJob.created_at)
    r = await db.execute(q)
    job = r.scalars().first()
    if job:
        job.status = "running"
        await db.commit()
        await db.refresh(job)
    return job

async def save_backtest_result(db: AsyncSession, job_id: int, result: Dict[str, Any]):
    q = update(BacktestJob).where(BacktestJob.id == job_id).values(result=result, status="finished")
    await db.execute(q)
    await db.commit()

async def mark_job_failed(db: AsyncSession, job_id: int, error: str):
    q = update(BacktestJob).where(BacktestJob.id == job_id).values(error=error, status="failed")
    await db.execute(q)
    await db.commit()

async def get_job(db: AsyncSession, job_id: int) -> Optional[BacktestJob]:
    q = select(BacktestJob).where(BacktestJob.id == job_id)
    r = await db.execute(q)
    return r.scalar_one_or_none()
