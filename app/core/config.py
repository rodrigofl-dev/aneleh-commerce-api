from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str
    api_version: str
    api_prefix: str
    environment: str
    cors_origins: str | List[str]

    mysql_database: str
    mysql_user: str
    mysql_password: str
    mysql_root_password: str
    database_url: str

    rabbitmq_url: str
    redis_url: str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expiration_seconds: int

    rate_limit_per_minute: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
