from pydantic_settings import BaseSettings
from pydantic import Field
from urllib.parse import quote
import os


class Settings(BaseSettings):
    # Individual DB components (preferred way)
    db_host: str = Field(default="localhost", validation_alias="DB_HOST")
    db_port: str = Field(default="5432", validation_alias="DB_PORT")
    db_user: str = Field(default="postgres", validation_alias="DB_USER")
    db_password: str = Field(default="", validation_alias="DB_PASSWORD")
    db_name: str = Field(default="demo", validation_alias="DB_NAME")
    
    api_base_url: str = Field(
        default="http://localhost:8000",
        validation_alias="API_BASE_URL"
    )
    environment: str = Field(
        default="development",
        validation_alias="ENVIRONMENT"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        # First check if DATABASE_URL is set directly (fallback)
        if database_url := os.getenv("DATABASE_URL"):
            return database_url
        
        # Otherwise, construct from individual components
        # Use quote() to escape special characters in password
        escaped_password = quote(self.db_password, safe='')
        
        if self.db_host == "localhost" and not self.db_password:
            # Local SQLite for development
            return f"sqlite:///./demo.db"
        
        # Use pooler.supabase.com with URL-encoded password for Python 3.13 + psycopg3
        # This avoids IPv6 resolution issues with direct db.hostname.supabase.co
        return f"postgresql+psycopg://{self.db_user}:{escaped_password}@aws-0-us-east-1.pooler.supabase.com:6543/{self.db_name}?statement_timeout=60000"


settings = Settings()