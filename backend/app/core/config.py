from pydantic import BaseSettings

class Settings(BaseSettings):
    # update this if you want a different DB user/password/host
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/backtester"
    ALLOW_ORIGINS: list = ["http://localhost:3000"]

settings = Settings()
