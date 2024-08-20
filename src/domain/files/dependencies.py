from typing import Any
from uuid import UUID

from .schemas import UniqueFieldsEnum
from .service import FilesService


service = FilesService()

validate_file = FilesService.get_instance_or_404

async def validate_file_id(file_id: UUID) -> dict[str, Any]:
    return await service.get_or_404(file_id, field=UniqueFieldsEnum.id)

async def validate_file_slug(file_slug: str) -> dict[str, Any]:
    return await service.get_or_404(file_slug, field=UniqueFieldsEnum.slug)

