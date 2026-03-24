"""Cinema router - API endpoints for Cinema entity."""
from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.modules.cinemas.service.cinema_service import CinemaServiceDep
from app.modules.cinemas.schemas.api import (
    CinemaCreateRequest,
    CinemaUpdateRequest,
    CinemaSearchRequest,
    CinemaResponse,
    CinemaListResponse,
    CinemaWithRoomsResponse,
)
from app.modules.cinemas.schemas.domain import (
    CinemaCreate,
    CinemaUpdate,
    CinemaSearchCriteria,
)
from app.modules.auth.dependencies import RequireAdmin
from app.shared.schemas.pagination import PaginationParams


router = APIRouter(prefix="/cinemas", tags=["Cinemas"])


@router.get(
    "",
    response_model=CinemaListResponse,
    summary="Danh sách rạp chiếu phim",
)
async def get_cinemas(
    service: CinemaServiceDep,
    city: str | None = None,
    params: PaginationParams = Depends(),
):
    if city:
        return await service.get_cinemas_by_city(city=city, pagination=params)

    return await service.get_cinemas(pagination=params)


@router.get(
    "/cities",
    response_model=list[str],
    summary="Danh sách thành phố có rạp",
)
async def get_cities(service: CinemaServiceDep):
    return await service.get_cities()


@router.get(
    "/search",
    response_model=list[CinemaResponse],
    summary="Tìm kiếm rạp chiếu phim",
)
async def search_cinemas(
    service: CinemaServiceDep,
    search: CinemaSearchRequest = Depends(),
    params: PaginationParams = Depends(),
):
    criteria = CinemaSearchCriteria(**search.model_dump(exclude_unset=True))

    results = await service.search_cinemas(criteria=criteria, pagination=params)

    return [CinemaResponse.model_validate(cinema) for cinema in results]


@router.get(
    "/{cinema_id}",
    response_model=CinemaResponse,
    summary="Chi tiết một rạp",
)
async def get_cinema(cinema_id: UUID, service: CinemaServiceDep):
    cinema = await service.get_cinema(cinema_id)

    return CinemaResponse.model_validate(cinema)


@router.get(
    "/{cinema_id}/detail",
    response_model=CinemaWithRoomsResponse,
    summary="Chi tiết rạp kèm danh sách phòng",
)
async def get_cinema_with_rooms(cinema_id: UUID, service: CinemaServiceDep):
    cinema = await service.get_cinema_with_rooms(cinema_id)

    return CinemaWithRoomsResponse.model_validate(cinema)


@router.post(
    "",
    response_model=CinemaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
    summary="Tạo rạp mới",
)
async def create_cinema(data: CinemaCreateRequest, service: CinemaServiceDep):
    cinema_data = CinemaCreate(**data.model_dump())

    cinema = await service.create_cinema(cinema_data)

    return CinemaResponse.model_validate(cinema)


@router.put(
    "/{cinema_id}",
    response_model=CinemaResponse,
    dependencies=[RequireAdmin],
    summary="Cập nhật thông tin rạp",
)
async def update_cinema(
    cinema_id: UUID,
    data: CinemaUpdateRequest,
    service: CinemaServiceDep,
):
    update_data = CinemaUpdate(**data.model_dump(exclude_unset=True))

    cinema = await service.update_cinema(cinema_id, update_data)

    return CinemaResponse.model_validate(cinema)


@router.delete(
    "/{cinema_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireAdmin],
    summary="Xoá rạp",
)
async def delete_cinema(cinema_id: UUID, service: CinemaServiceDep):
    await service.delete_cinema(cinema_id)


@router.patch(
    "/{cinema_id}/activate",
    response_model=CinemaResponse,
    dependencies=[RequireAdmin],
    summary="Kích hoạt rạp",
)
async def activate_cinema(cinema_id: UUID, service: CinemaServiceDep):
    cinema = await service.activate_cinema(cinema_id)

    return CinemaResponse.model_validate(cinema)


@router.patch(
    "/{cinema_id}/deactivate",
    response_model=CinemaResponse,
    dependencies=[RequireAdmin],
    summary="Vô hiệu hoá rạp",
)
async def deactivate_cinema(cinema_id: UUID, service: CinemaServiceDep):
    cinema = await service.deactivate_cinema(cinema_id)

    return CinemaResponse.model_validate(cinema)
