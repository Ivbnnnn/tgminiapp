from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    INFO_API_URL: str
    BASE_PRICE: int


settings = Settings()