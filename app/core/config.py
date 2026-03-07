from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Setting(BaseSettings):
    APP_NAME: str = "Movie-Booking"
    APP_ENV: str = "Development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_POST: str = "8000"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/namedb"

    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str = "SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000", "http://localhost:5173"]

    SEAT_LOCK_TTL: int = 900

    VNPAY_TMN_CODE: str
    VNPAY_HASH_SECRET: str
    VNPAY_PAYMENT_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL: str = "http://localhost:3000/payment/result"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_setting() -> Setting:
    return Setting()
