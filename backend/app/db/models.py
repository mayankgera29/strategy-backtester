from sqlalchemy import Column, Integer, String, JSON, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Strategy(Base):
    __tablename__ = "strategies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    graph = Column(JSON, nullable=False)   # serialized React Flow graph
    meta = Column(JSON, nullable=True)     # previously named 'metadata' — renamed to avoid conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BacktestJob(Base):
    __tablename__ = "backtest_jobs"
    id = Column(Integer, primary_key=True, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(String, default="queued", index=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
