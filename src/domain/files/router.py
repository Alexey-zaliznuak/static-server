import logging
import mimetypes
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi import File as FastAPIFile
from fastapi import (HTTPException, Request, Response,
                     UploadFile, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_restful.cbv import cbv

from external.yandex_disk import YandexDiskService
from infrastructure.auth import admin_access
from infrastructure.route.headers import NO_CACHE_HEADER

from src.domain.files.models import File
from src.infrastructure.rate_limit import limiter
from src.infrastructure.route.pagination import (PaginatedResponse,
                                                 PaginationParams,
                                                 get_pagination_params)

from .dependencies import validate_file, validate_file_id
from .schemas import FileCreate, FileGet, FileUpdate, UniqueFieldsEnum
from .service import FilesService


router = APIRouter(tags=["files"])
logger = logging.getLogger(__name__)


@cbv(router)
class FilesView:
    service = FilesService()
    yandex_disk_service = YandexDiskService()

    @router.get("/", response_model=PaginatedResponse[FileGet])
    @admin_access()
    async def get_all(
        self,
        request: Request,
        pagination: PaginationParams = Depends(get_pagination_params),
    ):
        return await PaginatedResponse.create(
            model=File,
            schema=FileGet,
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
            raise HTTPException(404, "No file")

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

    @router.patch("/{identifier}", response_model=FileGet)
    @admin_access()
    async def update(
        self,
        data: FileUpdate,
        request: Request,
        file: File = Depends(validate_file),
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

    @router.put("/{identifier}")
    @admin_access()
    async def upload(
        self,
        request: Request,
        background_tasks: BackgroundTasks,
        file: UploadFile = FastAPIFile(...),
        instance: File = Depends(validate_file),
    ):
        try:
            logger.info("Start file uploading: " + str(dict(instance)))

            upload_path, upload_url = await self.service.get_upload_data(instance, file)

            background_tasks.add_task(
                self.service.update_and_save_instance,
                instance=instance,
                data=dict(
                    path=upload_path,
                    size=file.size,
                    mime_type=file.content_type or mimetypes.guess_type(file.filename)[0]
                )
            )

            return RedirectResponse(url=upload_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        except ValueError:
            logger.error("Failed to upload: " + str(dict(instance)))
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Failed to upload")


    @router.delete("/{identifier}", response_model=None)
    @admin_access()
    async def delete(
        self,
        request: Request,
        file: File = Depends(validate_file),
    ):
        logger.warning("Delete file: " + str(dict(file)))

        await file.delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers={**NO_CACHE_HEADER})
