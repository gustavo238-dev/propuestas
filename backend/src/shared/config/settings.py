from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(
        default="postgresql+psycopg://imports:imports@postgres:5432/imports_db"
    )
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    allowed_origins: list[str] = Field(default=["http://localhost:3000"])
    storage_root: str = Field(default="/app/storage")
    smtp_host: str = Field(default="localhost")
    smtp_port: int = Field(default=1025)
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_sender: str = Field(default="operaciones@empresa-logistica.com")


settings = Settings()
