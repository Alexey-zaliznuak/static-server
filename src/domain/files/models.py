import mimetypes
import os
import uuid

from tortoise import fields
from tortoise.models import Model

from src.utils import slugify


class File(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, nullable=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    title = fields.CharField(max_length=100, nullable=True)
    slug = fields.CharField(max_length=100, unique=True, nullable=True, index=True)
    description = fields.TextField(nullable=True)

    path = fields.CharField(max_length=300, nullable=False)
    size = fields.IntField(nullable=False, description="Size in bytes")
    mime_type = fields.CharField(max_length=50, nullable=False)

    class Meta:
        indexes = [
            ("slug",),
            ("title",),
        ]

    @staticmethod
    def make_path(id: uuid.UUID, filename: str) -> str:
        """
        Generate file path based on UUID and filename.
        Example: <first 2 symbols of id>/<second 2 symbols of id>/<rest_of_id>.<extension>
        """
        id_str = str(id)
        extension = os.path.splitext(filename)[1]  # Get the file extension
        return f"{id_str[:2]}/{id_str[2:4]}/{id_str[4:]}{extension}"

    async def save(self, *args, **kwargs):
        if not self.slug:
            to_slugify = self.title or self.description
            self.slug=slugify(text=to_slugify, max_length=File.slug.max_length)

        if not self.mime_type and self.filename:
            self.mime_type = mimetypes.guess_type(self.filename)[0] or 'application/octet-stream'

        await super().save(*args, **kwargs)

    @property
    def filename(self) -> str:
        return os.path.basename(self.path)

    @property
    def directory(self) -> str:
        return os.path.dirname(self.path)
