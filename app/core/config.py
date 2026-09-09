from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./demo.db",
        validation_alias="DATABASE_URL"
    )
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


settings = Settings()