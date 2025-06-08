# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dasbor Auto Trade Bot API"
    API_V1_STR: str = "/api/v1"

    # Konfigurasi JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-default-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Kunci untuk enkripsi data sensitif (API Keys)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-default-encryption-key-32b")

    # Konfigurasi MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://root:07092004@mongodb:27017/")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "trading_bot_db")

    class Config:
        case_sensitive = True

settings = Settings()