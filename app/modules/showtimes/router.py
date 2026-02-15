"""Showtimes router - API endpoints cho module suất chiếu."""
from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.modules.showtimes.service import ShowtimeServiceDep
from app.modules.showtimes.schemas.api import (
    ShowtimeCreateRequest,
    ShowtimeUpdateRequest,
    ShowtimeResponse,
    ShowtimeListResponse,
    ShowtimeQueryParams,
    BulkShowtimeCreateRequest,
)
from app.modules.showtimes.schemas.domain import (
    ShowtimeCreate,
    ShowtimeUpdate,
    ShowtimeSearchCriteria,
)
from app.modules.auth.dependencies import RequireAdmin
from app.shared.schemas.pagination import PaginationParams


router = APIRouter(prefix="/showtimes", tags=["Showtimes"])


@router.get(
    "",
    response_model=ShowtimeListResponse,
    summary="Danh sách suất chiếu",
)
async def get_showtimes(
    service: ShowtimeServiceDep,
    query: ShowtimeQueryParams = Depends(),
    params: PaginationParams = Depends(),
):
    criteria = ShowtimeSearchCriteria(
        movie_id=query.movie_id,
        room_id=query.room_id,
        cinema_id=query.cinema_id,
        date_from=query.date_from,
        date_to=query.date_to,
        is_active=query.is_active,
    )

    items, total = await service.get_showtimes(
        criteria=criteria, pagination=params
    )

    return ShowtimeListResponse(
        items=[ShowtimeResponse.model_validate(item) for item in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.get(
    "/{showtime_id}",
    response_model=ShowtimeResponse,
    summary="Chi tiết suất chiếu",
)
async def get_showtime(showtime_id: UUID, service: ShowtimeServiceDep):
    showtime = await service.get_showtime(showtime_id)

    return ShowtimeResponse.model_validate(showtime)


@router.post(
    "",
    response_model=ShowtimeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
    summary="Tạo suất chiếu mới",
)
async def create_showtime(
    data: ShowtimeCreateRequest,
    service: ShowtimeServiceDep,
):
    create_data = ShowtimeCreate(
        movie_id=data.movie_id,
        room_id=data.room_id,
        start_time=data.start_time,
        end_time=data.end_time,
        base_price=data.base_price,
    )

    showtime = await service.create_showtime(create_data)

    return ShowtimeResponse.model_validate(showtime)


@router.post(
    "/bulk",
    response_model=list[ShowtimeResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
    summary="Tạo nhiều suất chiếu cùng lúc",
)
async def create_showtimes_bulk(
    data: BulkShowtimeCreateRequest,
    service: ShowtimeServiceDep,
):
    showtimes = await service.create_showtimes_bulk(data)

    return [ShowtimeResponse.model_validate(s) for s in showtimes]


@router.put(
    "/{showtime_id}",
    response_model=ShowtimeResponse,
    dependencies=[RequireAdmin],
    summary="Cập nhật suất chiếu",
)
async def update_showtime(
    showtime_id: UUID,
    data: ShowtimeUpdateRequest,
    service: ShowtimeServiceDep,
):
    update_data = ShowtimeUpdate(**data.model_dump(exclude_unset=True))

    showtime = await service.update_showtime(showtime_id, update_data)

    return ShowtimeResponse.model_validate(showtime)


@router.delete(
    "/{showtime_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireAdmin],
    summary="Xóa suất chiếu",
)
async def delete_showtime(showtime_id: UUID, service: ShowtimeServiceDep):
    await service.delete_showtime(showtime_id)


@router.patch(
    "/{showtime_id}/activate",
    response_model=ShowtimeResponse,
    dependencies=[RequireAdmin],
    summary="Kích hoạt suất chiếu",
)
async def activate_showtime(showtime_id: UUID, service: ShowtimeServiceDep):
    showtime = await service.activate_showtime(showtime_id)

    return ShowtimeResponse.model_validate(showtime)


@router.patch(
    "/{showtime_id}/deactivate",
    response_model=ShowtimeResponse,
    dependencies=[RequireAdmin],
    summary="Vô hiệu hoá suất chiếu",
)
async def deactivate_showtime(showtime_id: UUID, service: ShowtimeServiceDep):
    showtime = await service.deactivate_showtime(showtime_id)

    return ShowtimeResponse.model_validate(showtime)
