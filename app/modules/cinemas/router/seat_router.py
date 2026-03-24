"""Seat router - API endpoints for Seat entity."""
from fastapi import APIRouter, Depends, status
from uuid import UUID

from app.modules.cinemas.service.seat_service import SeatServiceDep
from app.modules.cinemas.models import SeatType
from app.modules.cinemas.schemas.api import (
    SeatUpdateRequest,
    BulkSeatUpdateRequest,
    SeatResponse,
)
from app.modules.cinemas.schemas.domain import (
    SeatUpdate,
    BulkSeatUpdate,
    SeatGenerationConfig,
)
from app.modules.auth.dependencies import RequireAdmin


router = APIRouter(prefix="/seats", tags=["Seats"])
room_seats_router = APIRouter(prefix="/rooms", tags=["Seats"])


@router.get(
    "/{seat_id}",
    response_model=SeatResponse,
    summary="Chi tiết một ghế",
)
async def get_seat(seat_id: UUID, service: SeatServiceDep):
    seat = await service.get_seat(seat_id)

    return SeatResponse.model_validate(seat)


@router.patch(
    "/bulk",
    response_model=list[SeatResponse],
    dependencies=[RequireAdmin],
    summary="Cập nhật nhiều ghế cùng lúc",
)
async def bulk_update_seats(data: BulkSeatUpdateRequest, service: SeatServiceDep):
    bulk_data = BulkSeatUpdate(**data.model_dump())

    seats = await service.bulk_update_seats(bulk_data)

    return [SeatResponse.model_validate(seat) for seat in seats]


@router.patch(
    "/{seat_id}",
    response_model=SeatResponse,
    dependencies=[RequireAdmin],
    summary="Cập nhật ghế",
)
async def update_seat(
    seat_id: UUID,
    data: SeatUpdateRequest,
    service: SeatServiceDep,
):
    update_data = SeatUpdate(**data.model_dump(exclude_unset=True))

    seat = await service.update_seat(seat_id, update_data)

    return SeatResponse.model_validate(seat)


@router.patch(
    "/{seat_id}/activate",
    response_model=SeatResponse,
    dependencies=[RequireAdmin],
    summary="Kích hoạt ghế",
)
async def activate_seat(seat_id: UUID, service: SeatServiceDep):
    seat = await service.activate_seat(seat_id)

    return SeatResponse.model_validate(seat)


@router.patch(
    "/{seat_id}/deactivate",
    response_model=SeatResponse,
    dependencies=[RequireAdmin],
    summary="Vô hiệu hoá ghế",
)
async def deactivate_seat(seat_id: UUID, service: SeatServiceDep):
    seat = await service.deactivate_seat(seat_id)

    return SeatResponse.model_validate(seat)


@room_seats_router.get(
    "/{room_id}/seats",
    response_model=list[SeatResponse],
    summary="Danh sách ghế trong phòng",
)
async def get_seats_by_room(room_id: UUID, service: SeatServiceDep):
    seats = await service.get_seats_by_room(room_id)

    return [SeatResponse.model_validate(seat) for seat in seats]


@room_seats_router.get(
    "/{room_id}/seats/by-type",
    response_model=list[SeatResponse],
    summary="Danh sách ghế theo loại",
)
async def get_seats_by_type(
    room_id: UUID,
    seat_type: SeatType,
    service: SeatServiceDep,
):
    seats = await service.get_seats_by_type(room_id, seat_type)

    return [SeatResponse.model_validate(seat) for seat in seats]


@room_seats_router.get(
    "/{room_id}/seats/count",
    summary="Đếm số ghế trong phòng",
)
async def count_seats(room_id: UUID, service: SeatServiceDep):
    count = await service.count_seats_by_room(room_id)

    return {"count": count}


@room_seats_router.post(
    "/{room_id}/seats/regenerate",
    response_model=list[SeatResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
    summary="Tạo lại toàn bộ ghế cho phòng",
)
async def regenerate_seats(
    room_id: UUID,
    config: SeatGenerationConfig,
    service: SeatServiceDep,
):
    seats = await service.generate_seats_for_room(room_id, config)

    return [SeatResponse.model_validate(seat) for seat in seats]


@room_seats_router.delete(
    "/{room_id}/seats",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireAdmin],
    summary="Xoá toàn bộ ghế trong phòng",
)
async def delete_seats_by_room(room_id: UUID, service: SeatServiceDep):
    await service.delete_seats_by_room(room_id)
