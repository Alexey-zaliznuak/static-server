import mimetypes
import os
import uuid

from pydantic import ValidationError
from tortoise import fields
from tortoise.models import Model

from src.utils import slugify
from utils import is_uuid


class File(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    title = fields.CharField(max_length=100, null=True)
    slug = fields.CharField(max_length=100, unique=True, null=True)
    description = fields.TextField(null=True)

    path = fields.CharField(max_length=300, null=True)
    size = fields.IntField(description="Size in bytes", null=True)
    mime_type = fields.CharField(max_length=50, null=True)

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
        self.clear()
        self.validate()
        await super().save(*args, **kwargs)

    def clear(self):
        if not self.slug:
            to_slugify = self.title or self.description
            self.slug=slugify(text=to_slugify, max_length=File.slug.max_length)

        if not self.mime_type and self.filename:
            self.mime_type = mimetypes.guess_type(self.filename)[0] or 'application/octet-stream'

    def validate(self):
        self.validate_slug(self.slug)

    def is_valid(self, *, use_clear: bool = True) -> bool:
        if use_clear:
            self.clear()

        try:
            self.validate()
            return True
        except:
            return False

    @staticmethod
    def validate_slug(value: str):
        if value and is_uuid(value):
            raise ValidationError(f"Slug can not be a UUID: {value}")

    @property
    def filename(self) -> str:
        return os.path.basename(self.path)

    @property
    def directory(self) -> str:
        return os.path.dirname(self.path)
