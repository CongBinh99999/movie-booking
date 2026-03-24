"""Room router - API endpoints for Room entity."""
from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.modules.cinemas.service.room_service import RoomServiceDep
from app.modules.cinemas.schemas.api import (
    RoomCreateRequest,
    RoomUpdateRequest,
    RoomResponse,
    RoomWithSeatsResponse,
)
from app.modules.cinemas.schemas.domain import RoomCreate, RoomUpdate
from app.modules.auth.dependencies import RequireAdmin
from app.shared.schemas.pagination import PaginationParams


router = APIRouter(prefix="/rooms", tags=["Rooms"])
cinema_rooms_router = APIRouter(prefix="/cinemas", tags=["Rooms"])


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Chi tiết một phòng chiếu",
)
async def get_room(room_id: UUID, service: RoomServiceDep):
    room = await service.get_room(room_id)

    return RoomResponse.model_validate(room)


@router.get(
    "/{room_id}/seats",
    response_model=RoomWithSeatsResponse,
    summary="Chi tiết phòng kèm sơ đồ ghế",
)
async def get_room_with_seats(room_id: UUID, service: RoomServiceDep):
    room = await service.get_room_with_seats(room_id)

    return RoomWithSeatsResponse.model_validate(room)


@cinema_rooms_router.get(
    "/{cinema_id}/rooms",
    response_model=list[RoomResponse],
    summary="Danh sách phòng chiếu của rạp",
)
async def get_rooms_by_cinema(
    cinema_id: UUID,
    service: RoomServiceDep,
    params: PaginationParams = Depends(),
):
    rooms = await service.get_rooms_by_cinema(cinema_id, params)

    return [RoomResponse.model_validate(room) for room in rooms]


@cinema_rooms_router.get(
    "/{cinema_id}/rooms/active",
    response_model=list[RoomResponse],
    summary="Danh sách phòng đang hoạt động",
)
async def get_active_rooms(cinema_id: UUID, service: RoomServiceDep):
    rooms = await service.get_active_rooms_by_cinema(cinema_id)

    return [RoomResponse.model_validate(room) for room in rooms]


@cinema_rooms_router.post(
    "/{cinema_id}/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
    summary="Tạo phòng chiếu mới",
)
async def create_room(
    cinema_id: UUID,
    data: RoomCreateRequest,
    service: RoomServiceDep,
):
    room_data = RoomCreate(**data.model_dump())

    room = await service.create_room(cinema_id, room_data)

    return RoomResponse.model_validate(room)


@router.put(
    "/{room_id}",
    response_model=RoomResponse,
    dependencies=[RequireAdmin],
    summary="Cập nhật phòng chiếu",
)
async def update_room(
    room_id: UUID,
    data: RoomUpdateRequest,
    service: RoomServiceDep,
):
    update_data = RoomUpdate(**data.model_dump(exclude_unset=True))

    room = await service.update_room(room_id, update_data)

    return RoomResponse.model_validate(room)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireAdmin],
    summary="Xoá phòng chiếu",
)
async def delete_room(room_id: UUID, service: RoomServiceDep):
    await service.delete_room(room_id)


@router.patch(
    "/{room_id}/activate",
    response_model=RoomResponse,
    dependencies=[RequireAdmin],
    summary="Kích hoạt phòng chiếu",
)
async def activate_room(room_id: UUID, service: RoomServiceDep):
    room = await service.activate_room(room_id)

    return RoomResponse.model_validate(room)


@router.patch(
    "/{room_id}/deactivate",
    response_model=RoomResponse,
    dependencies=[RequireAdmin],
    summary="Vô hiệu hoá phòng chiếu",
)
async def deactivate_room(room_id: UUID, service: RoomServiceDep):
    room = await service.deactivate_room(room_id)

    return RoomResponse.model_validate(room)
