from fastapi import APIRouter, Depends
from fastapi import File as FastAPIFile
from fastapi import (Header, HTTPException, Query, Request, Response,
                     UploadFile, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi_restful.cbv import cbv
from pydantic import ValidationError

from external.yandex_disk import YandexDiskService
from infrastructure.auth import admin_access
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
    yandex_disk_service = YandexDiskService()


    @router.get("/", response_model=PaginatedResponse[FileGet])
    @limiter.limit("10/minute")
    @admin_access()
    async def get_all(
        self,
        request: Request,
        pagination: PaginationParams = Depends(get_pagination_params),
    ):
        return await PaginatedResponse.create(
            model=File,
            pagination=pagination,
        )


    @router.get("/{identifier}/info", response_model=FileGet)
    @limiter.limit("10/minute")
    @admin_access()
    async def get_info(
        self,
        request: Request,
        file: File = Depends(validate_file)
    ):
        return file

    @router.get("/{identifier}")
    @limiter.limit("10/minute")
    async def download(
        self,
        request: Request,
        file: File = Depends(validate_file)
    ):
        return RedirectResponse(
            url = await self.yandex_disk_service.get_download_link(file.path)
        )

    @router.post("/", response_model=FileGet)
    @admin_access()
    async def create(self, data: FileCreate, request: Request):
        new_file = File(**data.model_dump())

        await new_file.validate_unique()
        await new_file.save()

        return FileGet.model_validate(new_file).model_dump()

    @router.patch("/{file_id}", response_model=FileGet)
    @admin_access()
    async def update_by_id(
        self,
        data: FileUpdate,
        request: Request,
        file: File = Depends(validate_file_id),
    ):
        file = file.update_from_dict(data.model_dump())

        await file.save()

        return JSONResponse(
            content=jsonable_encoder(file),
            status_code=status.HTTP_200_OK,
            headers={**NO_CACHE_HEADER}
        )

    @router.put("/{file_id}")
    @admin_access()
    async def upload_by_id(
        self,
        request: Request,
        file: UploadFile = FastAPIFile(...),
        instance: File = Depends(validate_file_id),
    ):
        try:
            content = await file.read()
            path = await self.service.upload_file(instance, file, content)

            instance = instance.update_from_dict(dict(
                (await self.service.get_file_metadata(file, content)).__dict__,
                path=path,
            ))

            await instance.save()

            return instance

        except ValidationError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Failed to upload")

    @router.delete("/{file_id}", response_model=None)
    @admin_access()
    async def delete_by_id(
        self,
        request: Request,
        file: File = Depends(validate_file_id),
    ):
        await file.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
