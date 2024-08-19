from tortoise.queryset import QuerySet
from tortoise.models import Model
from typing import Self, Type, TypeVar, Generic, List, Optional, Dict, overload
from pydantic import BaseModel
from fastapi import Query
from src.domain.files.models import File



T = TypeVar("T", bound=Model)


def get_pagination_params(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
) -> 'PaginationParams':
    return PaginationParams(page=page, size=size)


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1)
    size: int = Query(10, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    def apply_to_query(self, query: QuerySet[T]) -> QuerySet[T]:
        return query.limit(self.size).offset(self.offset)


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    page: int
    size: int
    total_items: int
    total_pages: int

    def __init__(self, data: List[T], pagination: PaginationParams, total_items: int):
        total_pages = (total_items + pagination.size - 1) // pagination.size
        super().__init__(
            data=data,
            page=pagination.page,
            size=min(len(data), pagination.size),
            total_items=total_items,
            total_pages=total_pages,
        )

    @classmethod
    async def create(
        cls,
        model: Type[T],
        pagination: PaginationParams,
        filters: Optional[Dict] = None,
    ) -> "PaginatedResponse[T]":
        query = model.all()

        if filters:
            query = query.filter(**filters)

        total_items = await query.count()

        paginated_query = pagination.apply_to_query(query)
        results = await paginated_query

        return cls(
            data=results,
            pagination=pagination,
            total_items=total_items,
        )

    class Config:
        arbitrary_types_allowed = True
