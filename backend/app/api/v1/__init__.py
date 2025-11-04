from fastapi import APIRouter
from . import strategies

router = APIRouter()
router.include_router(strategies.router)
