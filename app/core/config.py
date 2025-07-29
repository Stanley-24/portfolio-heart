from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Stanley Portfolio API"
    VERSION: str = "1.0.0"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 10000)) 
    DEBUG: bool = True
    
    # Database Configuration (from .env)
    POSTGRES_USER: str = "neondb_owner"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "neondb"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    BACKEND_URL : str
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?sslmode=require"
        )
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = [
        "https://stanley-o.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ]
    FRONTEND_URL: str = "https://stanley-o.vercel.app/"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # Email Configuration (for newsletter)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Zoho SMTP/email settings
    ZOHO_SMTP_SERVER: str = ""
    ZOHO_SMTP_PORT: int = 465
    ZOHO_SMTP_USER: str = ""
    ZOHO_SMTP_PASS: str = ""
    EMAIL_FROM: str = ""
    
    # Redis (for caching and background tasks)
    REDIS_URL: str = "redis://localhost:6379"
    
    OPENAI_API_KEY: str = ""
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    PYTHON_VERSION: Optional[str] = None
    
    # GeoIP Database
    GEOIP_DATABASE_PATH: Optional[str] = None
    
    # Google Calendar & OAuth
    GOOGLE_CALENDAR_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    GOOGLE_OAUTH_REDIRECT_URI: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create upload directory if it doesn't exist
