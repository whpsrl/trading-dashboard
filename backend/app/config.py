"""Application Configuration"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str
    
    # Security
    JWT_SECRET_KEY: str
    ENCRYPTION_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Market Data APIs
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    OANDA_API_TOKEN: str = ""
    FINNHUB_API_KEY: str = ""
    
    # AI
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    
    class Config:
        env_file = ".env"

settings = Settings()
