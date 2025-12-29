"""
Configuration Management
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Binance
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # App Settings
    TOP_N_COINS: int = 30
    MIN_CONFIDENCE_SCORE: int = 75
    MAX_ALERTS_PER_SCAN: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
