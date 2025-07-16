import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    mongo_url: str = "mongodb://localhost:27017/advanced_travel_db"
    database_name: str = "advanced_travel_db"
    
    # Security
    jwt_secret_key: str = "your-super-secret-jwt-key-for-advanced-travel-platform"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # API Keys (Optional)
    gemini_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()