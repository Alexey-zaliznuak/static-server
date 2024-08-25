import logging
import mimetypes
import os
from dataclasses import dataclass

from fastapi import HTTPException, UploadFile
from starlette import status

from domain.files.schemas import UniqueFieldsEnum
from external.yandex_disk import YandexDiskService
from src.domain.files.models import File
from src.utils import SingletonMeta


logger = logging.getLogger(__name__)


type upload_path = str
type upload_url = str


@dataclass
class FileMetadata:
    size: int
    mime_type: str


class FilesService(metaclass=SingletonMeta):
    yandex_disk_service = YandexDiskService()

    async def get_upload_data(self, instance: File, file: UploadFile) -> tuple[upload_path, upload_url]:
        new_path = self._make_file_path(instance, file)
        paths = dict(old=instance.path, new=new_path)

        logger.info("File paths: " + str(paths))

        yandex_disk_upload_url = await self.yandex_disk_service.get_upload_link(new_path)

        return new_path, yandex_disk_upload_url

    async def get_instance_or_404(self, identifier: str, field: UniqueFieldsEnum | None = UniqueFieldsEnum.id) -> File:
        field = field if field else UniqueFieldsEnum.id
        instance = None

        try:
            instance = await self.get_instance(identifier, field)

        except Exception:
            self.raise_not_found(identifier, field)

        if not instance:
            self.raise_not_found(identifier, field)

        return instance

    async def get_instance(self, identifier: str, field: UniqueFieldsEnum = UniqueFieldsEnum.id) -> File | None:
        return await File.filter(**{field: identifier}).first()

    async def get_file_metadata(self, file: UploadFile, file_content: bytes = None) -> FileMetadata:
        """
        :param: content content of file.read if it was call
        """
        file_content = await file.read() or file_content

        return FileMetadata(
            size = len(file_content),
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        )

    def raise_not_found(self, identifier: str, field: UniqueFieldsEnum = UniqueFieldsEnum.id):
        logger.error(f"Not found, {identifier=}, {field=}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    def _make_file_path(self, instance: File, file: UploadFile) -> str:
        """
        Generate file path based on UUID and filename.
        Example: <first 2 symbols of id>/<second 2 symbols of id>/<rest_of_id>.<extension>
        """
        id_str = str(instance.id)
        extension = os.path.splitext(file.filename)[1]

        return f"{id_str[:2]}/{id_str[2:4]}/{id_str[4:]}{extension}"
