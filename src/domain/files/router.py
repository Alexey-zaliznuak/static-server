import logging
from fastapi import APIRouter, Depends
from fastapi import File as FastAPIFile
from fastapi import (HTTPException, Request, Response,
                     UploadFile, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
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

from .dependencies import validate_file, validate_file_id
from .schemas import FileCreate, FileGet, FileUpdate
from .service import FilesService


router = APIRouter(tags=["files"])
logger = logging.getLogger(__name__)


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
        logger.info("Get file details: " + str(dict(file)))

        return JSONResponse(
            jsonable_encoder(FileGet.model_validate(file).model_dump()),
            headers={**NO_CACHE_HEADER}
        )

    @router.get("/{identifier}")
    @limiter.limit("10/minute")
    async def download(
        self,
        request: Request,
        file: File = Depends(validate_file)
    ):
        if not file.path:
            logger.info("Failed to download file - no path: " + str(dict(file)))
            raise HTTPException(404, "Not found")

        url = await self.yandex_disk_service.get_download_link(file.path)

        logger.info("Download file:" + str(dict(file, download_url = url)))
        return RedirectResponse(url = url)

    @router.post("/", response_model=FileGet)
    @admin_access()
    async def create(self, data: FileCreate, request: Request):
        new_file = File(**data.model_dump())

        await new_file.validate_unique()
        await new_file.save()

        new_file = FileGet.model_validate(new_file).model_dump()

        logger.info("Created file: " + str(new_file))

        return JSONResponse(
            jsonable_encoder(new_file),
            status_code=status.HTTP_201_CREATED,
            headers={**NO_CACHE_HEADER},
        )

    @router.patch("/{file_id}", response_model=FileGet)
    @admin_access()
    async def update_by_id(
        self,
        data: FileUpdate,
        request: Request,
        file: File = Depends(validate_file_id),
    ):
        logger.info("Update file", {
            "file": str(dict(file)),
            "data": data,
        })

        file = file.update_from_dict(data.model_dump())

        await file.save()

        return JSONResponse(
            content=jsonable_encoder(
                FileGet.model_validate(file).model_dump()
            ),
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
            logger.info("Start file uploading: " + str(dict(instance)))

            content = await file.read()
            path = await self.service.upload_file(instance, file, content)

            instance = instance.update_from_dict(dict(
                (await self.service.get_file_metadata(file, content)).__dict__,
                path=path,
            ))

            await instance.save()
            logger.info("Updated file after uploading: " + str(dict(instance)))

            return JSONResponse(
                jsonable_encoder(
                    FileGet.model_validate(instance).model_dump()
                ),
                headers={**NO_CACHE_HEADER}
            )

        except ValidationError:
            logger.error("Failed to upload: " + str(dict(file)))
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Failed to upload")

    @router.delete("/{file_id}", response_model=None)
    @admin_access()
    async def delete_by_id(
        self,
        request: Request,
        file: File = Depends(validate_file_id),
    ):
        logger.warning("Delete file: " + str(dict(file)))

        await file.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers={**NO_CACHE_HEADER})
