
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(".env", override=True)


class BaseConfig(BaseSettings):
    DATABASE_URL: str

    AUTHORIZATION_KEY: str


Config = BaseConfig()



TORTOISE_ORM = dict(
    connections=dict(
        default=Config.DATABASE_URL,  # Используем DATABASE_URL напрямую
    ),
    apps=dict(
        models=dict(
            models=[
                "aerich.models",
                "src.domain.files.models",
            ],
            default_connection="default",
        ),
    ),
)
