from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+psycopg://creatordna:creatordna@localhost:5432/creatordna"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,chrome-extension://*"

    api_secret_key: str | None = None
    auth_required: bool | None = None

    rate_limit_enabled: bool = True
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    upload_max_bytes: int = 100 * 1024 * 1024
    allowed_upload_content_types: str = "video/webm,audio/webm,audio/wav,audio/mpeg"

    media_ttl_hours: int = 48
    export_ttl_hours: int = 168

    ai_daily_quota: int = 500
    ai_cost_log_enabled: bool = True

    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 0.1

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

    @property
    def allowed_upload_types(self) -> set[str]:
        return {item.strip() for item in self.allowed_upload_content_types.split(",") if item.strip()}

    @property
    def is_auth_required(self) -> bool:
        if self.auth_required is not None:
            return self.auth_required
        if self.api_secret_key:
            return True
        return self.environment not in ("local", "test")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
