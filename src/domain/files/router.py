import os
from typing import Literal
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status
)
from fastapi.responses import FileResponse
from fastapi_restful.cbv import cbv

# from src.infrastructure.auth import admin_access
from src.infrastructure.rate_limit import limiter
from src.infrastructure.route.pagination import (
    PaginatedResponse,
    PaginationParams,
    get_pagination_params
)

from .config import FilesConfig as Config
from src.domain.files.models import File
from .schemas import (
    FileGet,
)
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

    # @router.get("/{identifier}/", response_model=GetPostResponse)
    # @limiter.limit("10/minute")
    # async def identifier(
    #     self,
    #     request: Request,
    #     identifier: str,  # TODO refactor
    #     field: UniqueFieldsEnum = Query(UniqueFieldsEnum.id),
    # ):
    #     try:
    #         if field == "id":
    #             return await self.service.get_by_id(identifier, self.session)
    #         if field == "slug":
    #             return await self.service.get_by_slug(identifier, self.session)

    #     except Exception as e:
    #         print(e)
    #         return Response("Not Found", status_code=status.HTTP_404_NOT_FOUND)

    # @router.get("/{post_slug}/files/content")
    # @limiter.limit("10/minute")
    # async def get_content_file(
    #     self,
    #     request: Request,
    #     post: File = Depends(validate_post_slug),
    # ):
    #     if post.content_file is None or not os.path.exists(post.content_file):
    #         raise HTTPException(status_code=404, detail="File not found")

    #     return FileResponse(path=post.content_file, media_type=Config.POSTS_CONTENT_FILE_MEDIA_TYPE)

    # @router.get("/{post_slug}/files/preview")
    # @limiter.limit("10/minute")
    # async def get_preview_file(
    #     self,
    #     request: Request,
    #     post: File = Depends(validate_post_slug),
    # ):
    #     if post.preview_file is None or not os.path.exists(post.preview_file):
    #         raise HTTPException(status_code=404, detail="File not found")

    #     return FileResponse(path=post.preview_file, media_type=Config.POSTS_CONTENT_FILE_MEDIA_TYPE)

    # @router.post("/", response_model=GetPostResponse)
    # @admin_access()
    # async def create_post(self, data: CreatePost, request: Request):
    #     new_post = File(
    #         title=data.title,
    #         slug=await File.generate_slug(data.title, self.session),
    #         short_description=data.short_description,
    #         reading_time=data.reading_time,
    #     )

    #     await self.service.save_and_refresh(new_post, self.session)

    #     if not new_post:
    #         raise HTTPException(status.HTTP_409_CONFLICT, "Failed to create post")

    #     return new_post

    # @router.patch("/{post_id}", response_model=GetPostResponse)
    # @admin_access()
    # async def update_by_id(
    #     self,
    #     data: UpdatePost,
    #     request: Request,
    #     post: File = Depends(validate_post_id),
    # ):
    #     await self.service.update_instance_fields(
    #         post,
    #         data=data.model_dump(exclude_unset=True),
    #         session=self.session,
    #         save=True,
    #     )
    #     return post

    # @router.put("/{post_id}/files/content", response_model=GetPostResponse)
    # @admin_access()
    # async def upload_post_content_file(
    #     self,
    #     request: Request,
    #     file: UploadFile = File(...),
    #     post: File = Depends(validate_post_id),
    # ):
    #     await self.service.update_instance_fields(
    #         post,
    #         data={"content_file": await self.service.save_content_file(post.id, file)},
    #         session=self.session,
    #         save=True,
    #     )
    #     return post

    # @router.put("/{post_id}/files/preview", response_model=GetPostResponse)
    # @admin_access()
    # async def upload_post_preview_file(
    #     self,
    #     request: Request,
    #     file: UploadFile = File(...),
    #     post: File = Depends(validate_post_id),
    # ):
    #     await self.service.update_instance_fields(
    #         post,
    #         data={"preview_file": await self.service.save_preview_file(post.id, file)},
    #         session=self.session,
    #         save=True,
    #     )
    #     return post

    # @router.delete("/{post_id}", response_model=None)
    # @admin_access()
    # async def delete_post_by_id(
    #     self,
    #     request: Request,
    #     post: BasicPost = Depends(validate_post_id),
    # ):
    #     try:
    #         await self.service.delete_by_id(post.id, post.file, self.session)

    #     except FileNotFoundError:
    #         print("FILE NOT FOUND", post.file, flush=True)
    #         raise

    #     return Response(status_code=status.HTTP_204_NO_CONTENT)
