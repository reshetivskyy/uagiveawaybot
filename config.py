# import os
# from dotenv import load_dotenv

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# DB_URL = os.getenv("DB_URL")

from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_URL: str
    ADMINS: List[int]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
