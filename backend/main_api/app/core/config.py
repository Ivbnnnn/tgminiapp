from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_AUTH_MAX_AGE_SECONDS: int = 3600

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "product-photos"
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_URL: str 
    MAX_PHOTO_SIZE_BYTES: int = 10 * 1024 * 1024

    CORS_ORIGINS: str 
    ADMIN_TELEGRAM_IDS: str 
    COOKIE_SECURE: bool 

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def admin_telegram_ids(self) -> set[int]:
        return {
            int(value.strip())
            for value in self.ADMIN_TELEGRAM_IDS.split(",")
            if value.strip()
        }


settings = Settings()
