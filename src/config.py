from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from dotenv import load_dotenv


load_dotenv(".env", override=True)


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn
