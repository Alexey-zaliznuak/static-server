import asyncio
from functools import wraps
import os
from time import time
import yadisk
import aiohttp
from .config import YandexDiskConfig as Config
from fastapi import UploadFile
from utils import SingletonMeta
import logging


logger = logging.getLogger(__name__)


def handle_unauthorized_error(method):
    """
    Recall method if UnauthorizedError was raise.
    """
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        try:
            return await method(self, *args, **kwargs)

        except yadisk.exceptions.UnauthorizedError:
            await YandexDiskService().init_client()
            return await method(self, *args, **kwargs)

    return wrapper

def handle_check_client(method):
    """
    Call YandexDiskService().init_client() if check_token failed.
    """
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        if not await YandexDiskService().client.check_token():
            await YandexDiskService().init_client()

        return await method(self, *args, **kwargs)

    return wrapper


class YandexDiskService(metaclass=SingletonMeta):
    client = yadisk.AsyncClient()

    async def init(self,):
        await self.init_client()

    async def init_client(self):
        """
        Init client with new access token.
        """
        new_token = await self._get_new_access_token()
        self.client = yadisk.AsyncClient(token=new_token)

    @handle_unauthorized_error
    @handle_check_client
    async def upload_file(self, content: bytes, path: str):
        await self.create_directory(os.path.dirname(path))

        upload_link = await self.client.get_upload_link(path, overwrite=True)

        async with aiohttp.ClientSession() as session:
            async with session.put(upload_link, data=content) as response:
                response.raise_for_status()
                print(f"Create file: {path}")

    async def create_directory(self, dir_path: str):
        dirs = dir_path.split("/")
        current_path = ""

        for dir_name in dirs:
            if dir_name:
                current_path += f"/{dir_name}"

                try:
                    await self.client.mkdir(current_path)
                    print(f"Create directory: {current_path}")

                except yadisk.exceptions.DirectoryExistsError:
                    pass

                except Exception as e:
                    raise e

    async def _get_new_access_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "/".join([Config.YANDEX_API_OAUTH_BASE_URL, "token"]),
                data=dict(
                    grant_type="refresh_token",
                    refresh_token=Config.YANDEX_API_REFRESH_TOKEN,
                    client_id=Config.YANDEX_API_CLIENT_ID,
                    client_secret=Config.YANDEX_API_CLIENT_SECRET,
                )
            ) as response:
                response_data = await response.json()
                return response_data.get("access_token")

    async def create_refresh_token(self, code: str):
        """
        Used for getting refresh token. Only for development.
        Code gets on https://oauth.yandex.ru/authorize?response_type=code&client_id=<client_id>
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "/".join([Config.YANDEX_API_OAUTH_BASE_URL, "token"]),
                data=dict(
                    grant_type="authorization_code",
                    code=code,
                    client_id=Config.YANDEX_API_CLIENT_ID,
                    client_secret=Config.YANDEX_API_CLIENT_SECRET,
                )
            ) as response:
                return await response.json()

    @handle_unauthorized_error
    @handle_check_client
    async def get_download_link(self, path: str):
        link = await self.client.get_download_link(path)

        print(f"New link recieved: {link}, {path=}")

        return link

    @handle_unauthorized_error
    @handle_check_client
    async def remove(self, path: str, *, throw_not_found: bool = True):
        try:
            await self.client.remove(path)
            print(f"Remove object: {path}")

        except Exception as e:
            if throw_not_found:
                print(f"Failed when remove resource: {path}")
                raise e

            print(f"Resource not found: {path}")
