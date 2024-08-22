from typing import Literal

from dotenv import load_dotenv

from config import BaseConfig

load_dotenv(override=True)


class YandexDiskConfig(BaseConfig):
    YANDEX_API_REFRESH_TOKEN: str
    YANDEX_API_CLIENT_ID: str
    YANDEX_API_CLIENT_SECRET: str

    YANDEX_API_OAUTH_BASE_URL: Literal["https://oauth.yandex.ru"] = "https://oauth.yandex.ru"


YandexDiskConfig = YandexDiskConfig()
