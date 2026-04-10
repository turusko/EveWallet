from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://user:pass@localhost:5432/eve_tracker"
    secret_key: str = "change_me"

    eve_client_id: str = ""
    eve_client_secret: str = ""
    eve_redirect_uri: str = "http://localhost:8000/auth/callback"
    eve_sso_authorize_url: str = "https://login.eveonline.com/v2/oauth/authorize"
    eve_sso_token_url: str = "https://login.eveonline.com/v2/oauth/token"
    eve_esi_base_url: str = "https://esi.evetech.net/latest"
    eve_scopes: str = Field(
        default=(
            "esi-wallet.read_character_wallet.v1 "
            "esi-markets.read_character_orders.v1 "
            "esi-wallet.read_character_wallet.v1"
        )
    )
    token_encryption_key: str | None = None

    redis_url: str = "redis://localhost:6379/0"
    sync_use_background_worker: bool = True
    sync_interval_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()
