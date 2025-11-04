from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.db.session import get_db
from app.db import crud
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class StrategyIn(BaseModel):
    name: str
    graph: Dict[str, Any]
    metadata: Dict[str, Any] = None

class StrategyOut(BaseModel):
    id: int
    name: str

@router.post("/strategies", response_model=StrategyOut)
async def create_strategy(payload: StrategyIn, db: AsyncSession = Depends(get_db)):
    s = await crud.create_strategy(db, payload.dict())
    return {"id": s.id, "name": s.name}

@router.get("/strategies", response_model=list[StrategyOut])
async def get_strategies(db: AsyncSession = Depends(get_db)):
    rows = await crud.list_strategies(db)
    return [{"id": r.id, "name": r.name} for r in rows]

# Backtest endpoints
class BacktestRequest(BaseModel):
    strategy_id: int
    symbol: str
    start: str
    end: str
    timeframe: str = "1m"
    params: Dict[str, Any] = None
    force_close: bool = True

@router.post("/backtests")
async def start_backtest(req: BacktestRequest, db: AsyncSession = Depends(get_db)):
    # ensure strategy exists
    s = await crud.get_strategy(db, req.strategy_id)
    if not s:
        raise HTTPException(status_code=404, detail="Strategy not found")
    job_payload = {
        "strategy_id": req.strategy_id,
        "symbol": req.symbol,
        "start": req.start,
        "end": req.end,
        "timeframe": req.timeframe,
        "params": req.params or {},
        "force_close": req.force_close
    }
    job = await crud.create_backtest_job(db, job_payload)
    return {"job_id": job.id, "status": job.status}

@router.get("/backtests/{job_id}")
async def get_backtest(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "status": job.status,
        "result": job.result,
        "error": job.error,
        "payload": job.payload,
        "created_at": job.created_at.isoformat()
    }
