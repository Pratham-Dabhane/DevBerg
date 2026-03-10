from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/devberg"
    github_token: str = ""
    stackoverflow_api_key: str = ""
    collection_interval_hours: int = 12

    tracked_technologies: list[dict[str, str]] = []  # populated from DB at runtime

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
