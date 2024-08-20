import os
from typing import Literal
from uuid import UUID

from fastapi import (APIRouter, Depends, File, Header, HTTPException, Query,
                     Request, Response, UploadFile, status)
from fastapi.responses import FileResponse
from fastapi_restful.cbv import cbv

# from src.infrastructure.auth import admin_access
from infrastructure.route.headers import NO_CACHE_HEADER
from src.domain.files.models import File
from src.infrastructure.rate_limit import limiter
from src.infrastructure.route.pagination import (PaginatedResponse,
                                                 PaginationParams,
                                                 get_pagination_params)

from .config import FilesConfig as Config
from .dependencies import validate_file, validate_file_id
from .schemas import FileCreate, FileGet, FileUpdate, UniqueFieldsEnum
from .service import FilesService

router = APIRouter(tags=["files"])


@cbv(router)
class FilesView:
    service = FilesService()

    @router.get("/", response_model=PaginatedResponse[FileGet])
    @limiter.limit("10/minute")
    async def get_all(
        self,
        request: Request,
        pagination: PaginationParams = Depends(get_pagination_params),
    ):
        return await PaginatedResponse.create(
            model=File,
            pagination=pagination,
        )

    @router.get("/{identifier}/", response_model=FileGet)
    @limiter.limit("10/minute")
    async def identifier(
        self,
        request: Request,
        file: File = Depends(validate_file)
    ):
        return file

    @router.post("/", response_model=FileGet)
    async def create(self, data: FileCreate, request: Request):
        new_file = File(**data)

        await new_file.save()

        return Response(new_file, status.HTTP_201_CREATED)

    @router.patch("/{file_id}", response_model=FileGet)
    async def update_by_id(
        self,
        data: FileUpdate,
        request: Request,
        file: File = Depends(validate_file_id),
    ):
        file = file.update_from_dict(data)

        await file.save()

        return Response(file, status.HTTP_200_OK, headers={**NO_CACHE_HEADER})

    @router.put("/{file_id}/files/preview", response_model=G)
    async def upload(
        self,
        request: Request,
        upload_file: UploadFile = File(...),
        file_instance: File = Depends(validate_file_id),
    ):
        try:
            path = await self.service.upload_file(file_instance, upload_file)

        except:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Failed to upload")

        file_instance = file_instance.update_from_dict(dict(
            path=path,
            **await self.service.get_file_metadata(upload_file)
        ))

    @router.delete("/{file_id}", response_model=None)
    async def delete_by_id(
        self,
        request: Request,
        file: File = Depends(validate_file_id),
    ):
        await file.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
