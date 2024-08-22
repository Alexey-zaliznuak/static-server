import mimetypes
import os
import uuid
from string import ascii_letters, digits

from fastapi import HTTPException
from starlette import status
from tortoise import fields
from tortoise.expressions import Q
from tortoise.models import Model

from src.utils import is_uuid, slugify


AVAILABLE_SLUG_CHARS = ascii_letters + digits + "-"


class File(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    title = fields.CharField(max_length=100, null=True)
    slug = fields.CharField(max_length=100, unique=True, null=True)
    description = fields.TextField(null=True)

    path = fields.CharField(max_length=300, null=True)
    size = fields.IntField(description="Size in bytes", null=True)
    mime_type = fields.CharField(max_length=200, null=True)

    class Meta:
        indexes = [
            ("slug",),
            ("title",),
        ]

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

    async def validate_unique(self):
        """
        Use before create to check constraints.
        """
        existing_record = await self.filter(Q(id=self.id) | Q(slug=self.slug)).exists()

        if existing_record:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Record with provided unique fields already exists")

    @staticmethod
    def validate_slug(value: str):
        if value and is_uuid(value):
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Slug can not be a UUID: {value}")

        for char in value:
            if char not in AVAILABLE_SLUG_CHARS:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"Invalid slug: {value}, available chars: '{AVAILABLE_SLUG_CHARS}'"
                )

    @property
    def filename(self) -> str | None:
        if not self.path:
            return None

        return os.path.basename(self.path)

    @property
    def directory(self) -> str | None:
        if not self.path:
            return None

        return os.path.dirname(self.path)
