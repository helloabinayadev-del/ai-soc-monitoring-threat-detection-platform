import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise AI SOC Monitoring & Threat Detection Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Auth Configuration
    SECRET_KEY: str = "SOC_SECRET_KEY_SUPER_SECURE_9876543210_ENTERPRISE_SECURE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "soc_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "soc_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "soc_monitoring_db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Database URL
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    ASYNC_DATABASE_URI: Optional[str] = None

    # Elasticsearch Configuration
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if not self.ASYNC_DATABASE_URI:
            self.ASYNC_DATABASE_URI = f"sqlite+aiosqlite:///./soc_platform.db" # Default fallback for local standalone mode if Postgres not configured

settings = Settings()
