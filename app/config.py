from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    payment_webhook_secret: str = "dev-payment-webhook-secret"
    ranking_provider: str = "local"
    n8n_ranking_webhook_url: str | None = None
    n8n_ranking_timeout_seconds: float = 2.5
    n8n_ranking_fallback_enabled: bool = True
    n8n_ranking_auth_header: str | None = None
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 10080
    db_pool_min_size: int = 1
    db_pool_max_size: int = 10


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _require_env_any(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    joined_names = ", ".join(names)
    raise RuntimeError(f"Missing required environment variable. Set one of: {joined_names}")


def get_settings() -> Settings:
    ranking_provider = os.getenv("RANKING_PROVIDER", "local").strip().lower()
    fallback_raw = os.getenv("N8N_RANKING_FALLBACK_ENABLED", "true").strip().lower()
    fallback_enabled = fallback_raw in {"1", "true", "yes", "on"}

    return Settings(
        database_url=_require_env_any("DATABASE_URL", "DB_URL"),
        jwt_secret=_require_env("JWT_SECRET"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        payment_webhook_secret=os.getenv("PAYMENT_WEBHOOK_SECRET", "dev-payment-webhook-secret"),
        ranking_provider=ranking_provider,
        n8n_ranking_webhook_url=os.getenv("N8N_RANKING_WEBHOOK_URL"),
        n8n_ranking_timeout_seconds=float(os.getenv("N8N_RANKING_TIMEOUT_SECONDS", "2.5")),
        n8n_ranking_fallback_enabled=fallback_enabled,
        n8n_ranking_auth_header=os.getenv("N8N_RANKING_AUTH_HEADER"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        refresh_token_expire_minutes=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080")),
        db_pool_min_size=int(os.getenv("DB_POOL_MIN_SIZE", "1")),
        db_pool_max_size=int(os.getenv("DB_POOL_MAX_SIZE", "10")),
    )
