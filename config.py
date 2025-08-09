from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_URL: str
    ADMINS: List[int]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
