from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings
from typing import List
from urllib.parse import quote_plus
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dome"
    API_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    CRYPT_ALGO: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # MongoDB settings
    MONGO_PW: str = "password"
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "dome"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
settings.MONGO_URI = settings.MONGO_URI.format(password=quote_plus(settings.MONGO_PW))