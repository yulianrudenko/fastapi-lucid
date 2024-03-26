from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str
    CACHE_URL: str

settings = Settings()
