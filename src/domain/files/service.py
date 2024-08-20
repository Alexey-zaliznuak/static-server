import mimetypes
from fastapi import HTTPException, UploadFile
from domain.files.schemas import UniqueFieldsEnum
from src.utils import SingletonMeta
from .models import File
from starlette import status
from dataclasses import dataclass


@dataclass
class FileMetadata:
    size: int
    mime_type: str


class FilesService(metaclass=SingletonMeta):

    async def upload_file(self, instance: File, file: UploadFile) -> str:
        pass

    async def get_instance_or_404(self, identifier: str, field: UniqueFieldsEnum | None = UniqueFieldsEnum.id) -> File:
        field = field if field else UniqueFieldsEnum.id

        instance = self.get_instance(identifier, field)

        if not instance:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

        return instance

    async def get_instance(self, identifier: str, field: UniqueFieldsEnum = UniqueFieldsEnum.id) -> File | None:
        return await File.filter(**{field: identifier}).first()

    async def get_file_metadata(self, file: UploadFile) -> FileMetadata:
        content = await file.read()

        return FileMetadata(
            file_size = len(content),
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        )
