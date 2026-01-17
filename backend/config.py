from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    google_api_key: str
    environment: str = "development"
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    worker_url: str
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
