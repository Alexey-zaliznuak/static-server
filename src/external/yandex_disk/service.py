import logging
import os
from functools import wraps

import aiohttp
import yadisk

from utils import SingletonMeta

from .config import YandexDiskConfig as Config


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
            logger.warning(f"Get UnauthorizedError, recall method: {method.__name__}")

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
        logger.info("Start client init")

        new_token = await self._get_new_access_token()
        self.client = yadisk.AsyncClient(token=new_token)

        logger.info("Client successfully recreated")


    @handle_unauthorized_error
    @handle_check_client
    async def upload_file(self, content: bytes, path: str):
        logger.info(f"Start file uploading: {path}")

        await self.create_directory(os.path.dirname(path))

        upload_link = await self.client.get_upload_link(path, overwrite=True)

        logger.info(f"Got file download link: {path}")

        async with aiohttp.ClientSession() as session:
            async with session.put(upload_link, data=content) as response:
                response.raise_for_status()
                logger.info(f"Create file: {path}")

    @handle_unauthorized_error
    @handle_check_client
    async def create_directory(self, dir_path: str):
        dirs = dir_path.split("/")
        current_path = ""

        for dir_name in dirs:
            if dir_name:
                current_path += f"/{dir_name}"

                try:
                    await self.client.mkdir(current_path)
                    logger.info(f"Create directory: {current_path}")

                except yadisk.exceptions.DirectoryExistsError:
                    pass

                except Exception as e:
                    raise e

    @handle_unauthorized_error
    @handle_check_client
    async def get_download_link(self, path: str):
        link = await self.client.get_download_link(path)

        logger.info(f"New link recieved for {path}: {link}")

        return link

    @handle_unauthorized_error
    @handle_check_client
    async def remove(self, path: str, *, throw_not_found: bool = True):
        try:
            await self.client.remove(path)
            logger.warning(f"Removed object: {path}")

        except yadisk.exceptions.NotFoundError as e:
            if throw_not_found:
                logger.error(f"Failed when remove object: {path}")
                raise e

            logger.warning(f"Resource not found: {path}")

    @handle_unauthorized_error
    @handle_check_client
    async def get_upload_link(self, path: str):
        """
        Get link for file uploading.
        Recursively creates directories.
        """

        try:
            await self.create_directory(os.path.dirname(path))
            upload_url = await self.client.get_upload_link(path, overwrite=True)

            if upload_url:
                return upload_url

            logger.error("Failed to generate upload URL")

        except yadisk.exceptions.PathNotFoundError as e:
            logger.error(f"Path not found on Yandex Disk: {path}")
            raise e

        except yadisk.exceptions.YaDiskError as e:
            logger.error(f"Error generating Yandex Disk upload URL: {str(e)}")
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
                access_token = response_data.get("access_token")

                logger.debug(f"Created new access token: {access_token}")
                return access_token

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
