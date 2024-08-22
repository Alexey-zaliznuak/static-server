from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UniqueFieldsEnum(str, Enum):
    id = "id"
    slug = "slug"


class FileCreate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example title",
                "slug": "example-slug",
                "description": "This is an example file.",
            }
        }


class FileUpdate(FileCreate):
    pass


class FileGet(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

    mime_type: Optional[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2024-08-19T12:34:56.123456",
                "updated_at": "2024-08-19T12:34:56.123456",
                "title": "Example title",
                "slug": "example-slug",
                "description": "This is an example file.",
                "size": 12345,
                "mime_type": "text/plain",
            }
        }
