from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = "development"

    # Falls back to a local SQLite file so the app runs with zero external
    # services for local dev; production sets DATABASE_URL to Postgres.
    DATABASE_URL: str = "sqlite:///./dev.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "dev-only-insecure-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PAYMENT_PROVIDER: str = "razorpay"
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    STORAGE_PROVIDER: str = "s3"
    AWS_S3_BUCKET: str = ""
    AWS_REGION: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # "gemini" (free tier via aistudio.google.com) or "anthropic".
    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-3.6-flash"

    # Transactional email via Resend's HTTP API — not raw SMTP, because
    # Render's free tier blocks outbound SMTP ports (25/465/587) entirely,
    # so a real mail server is unreachable from there regardless of
    # credentials. Get a free API key at resend.com. RESEND_FROM_EMAIL must
    # be an address on a domain verified in your Resend account (their
    # shared onboarding@resend.dev sandbox address only delivers to your
    # own Resend account email until you verify a domain).
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "EduSphere CBSE <onboarding@resend.dev>"

    # Shared secret for endpoints triggered by an external scheduler (e.g. a
    # scheduled GitHub Actions workflow) rather than a logged-in user —
    # Render's free tier has no built-in cron. Left empty by default, which
    # makes those endpoints refuse every request until explicitly set.
    CRON_SECRET: str = ""

    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
