# backend/app/api/v1/strategies.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

router = APIRouter(tags=["strategies"])

class StrategyIn(BaseModel):
    name: str
    graph: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class StrategyOut(BaseModel):
    id: int
    name: str
    graph: Dict[str, Any]
    metadata: Dict[str, Any] = {}

# in-memory store (replace with DB in production)
_store: List[Dict[str, Any]] = []
_next_id = 1

@router.post("/strategies", response_model=StrategyOut)
async def create_strategy(payload: StrategyIn):
    global _next_id
    item = {"id": _next_id, "name": payload.name, "graph": payload.graph, "metadata": payload.metadata}
    _store.append(item)
    _next_id += 1
    return item

@router.get("/strategies")
async def list_strategies():
    # return minimal info list (id + name) — frontend expects list of objects
    return [{"id": s["id"], "name": s["name"]} for s in _store]

@router.get("/strategies/{strategy_id}", response_model=StrategyOut)
async def get_strategy(strategy_id: int):
    for s in _store:
        if s["id"] == strategy_id:
            return s
    raise HTTPException(status_code=404, detail="Strategy not found")
