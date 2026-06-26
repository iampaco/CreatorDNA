from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://creatordna:creatordna@localhost:5432/creatordna"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,chrome-extension://*"

    storage_endpoint: str = "http://localhost:9000"
    storage_access_key: str = "minioadmin"
    storage_secret_key: str = "minioadmin"
    storage_bucket: str = "creator-dna"
    storage_region: str = "auto"

    openai_api_key: str | None = None
    openai_asr_model: str = "whisper-1"
    openai_chat_model: str = "gpt-4o-mini"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
