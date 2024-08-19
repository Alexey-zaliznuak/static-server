from typing import Any, override
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from dotenv import load_dotenv


load_dotenv(".env", override=True)


class Config(BaseSettings):
    DATABASE_URL: str


Config = Config()


TORTOISE_ORM_CONFIG = dict(
    connections = dict(
        default = Config.DATABASE_URL,
    ),
    apps = dict(
        models = dict(
            models = ["aerich.models"],
            default_connection = "default"
        )
    )
)
