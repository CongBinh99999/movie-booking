from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.auth.dependencies import CurrentUser, RequireAdmin
from app.modules.bookings.exceptions import BookingNotFoundError
from app.modules.bookings.models import BookingStatus
from app.modules.bookings.schemas.api import (
    BookingCreateRequest,
    BookingCancelRequest,
    BookingListResponse,
    BookingCalculationResponse,
    CalculateBookingRequest,
    SeatAvailabilityResponse,
    UpdateBookingStatusRequest,
)
from app.modules.bookings.schemas.domain import BookingDTO
from app.modules.bookings.service import BookingServiceDep
from app.shared.schemas.pagination import PaginationParams

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo đơn đặt vé mới",
)
async def create_booking(
    data: BookingCreateRequest,
    current_user: CurrentUser,
    service: BookingServiceDep,
):
    return await service.create_booking(
        user_id=current_user.id,
        showtime_id=data.showtime_id,
        seat_ids=data.seat_ids,
    )


@router.get(
    "",
    response_model=BookingListResponse,
    summary="Danh sách đơn đặt vé của tôi",
)
async def get_my_bookings(
    current_user: CurrentUser,
    service: BookingServiceDep,
    params: PaginationParams = Depends(),
):
    items, total = await service.get_user_bookings(
        user_id=current_user.id,
        skip=params.offset,
        limit=params.size,
    )

    return BookingListResponse(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
    )


@router.post(
    "/calculate",
    response_model=BookingCalculationResponse,
    summary="Tính giá đặt vé",
)
async def calculate_booking(
    data: CalculateBookingRequest,
    current_user: CurrentUser,
    service: BookingServiceDep,
):
    calculation = await service.calculate_booking_total(
        showtime_id=data.showtime_id,
        seat_ids=data.seat_ids,
    )

    return BookingCalculationResponse(
        seats=calculation.seats,
        total_amount=calculation.total_amount,
    )


@router.get(
    "/code/{booking_code}",
    response_model=BookingDTO,
    summary="Tra cứu đơn đặt vé theo mã",
)
async def get_booking_by_code(
    booking_code: str,
    current_user: CurrentUser,
    service: BookingServiceDep,
):
    return await service.get_booking_by_code(
        booking_code=booking_code,
        user_id=current_user.id,
    )


@router.get(
    "/{booking_id}",
    response_model=BookingDTO,
    summary="Chi tiết đơn đặt vé",
)
async def get_booking_by_id(
    booking_id: UUID,
    current_user: CurrentUser,
    service: BookingServiceDep,
):
    return await service.get_booking_by_id(
        booking_id=booking_id,
        user_id=current_user.id,
    )


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingDTO,
    summary="Hủy đơn đặt vé",
)
async def cancel_booking(
    booking_id: UUID,
    current_user: CurrentUser,
    service: BookingServiceDep,
    data: BookingCancelRequest | None = None,
):
    reason = data.cancellation_reason if data else None

    return await service.cancel_booking(
        booking_id=booking_id,
        user_id=current_user.id,
        reason=reason,
    )


seat_router = APIRouter(prefix="/showtimes", tags=["Bookings"])


@seat_router.get(
    "/{showtime_id}/seats",
    response_model=SeatAvailabilityResponse,
    summary="Danh sách ghế theo suất chiếu",
)
async def get_seat_availability(
    showtime_id: UUID,
    service: BookingServiceDep,
):
    seats = await service.get_available_seats(showtime_id)
    base_price = seats[0].base_price if seats else 0

    return SeatAvailabilityResponse(
        showtime_id=showtime_id,
        base_price=base_price,
        seats=seats,
    )


admin_router = APIRouter(
    prefix="/admin/bookings",
    tags=["Admin - Bookings"],
    dependencies=[RequireAdmin],
)


@admin_router.get(
    "",
    response_model=BookingListResponse,
    summary="[Admin] Danh sách tất cả đơn đặt vé",
)
async def admin_get_bookings(
    service: BookingServiceDep,
    status_filter: BookingStatus | None = Query(
        None, alias="status",
    ),
    showtime_id: UUID | None = Query(None),
    params: PaginationParams = Depends(),
):
    if showtime_id:
        items = await service.booking_repo.get_by_showtime(
            showtime_id, skip=params.offset, limit=params.size,
        )
        total = await service.booking_repo.count_by_showtime(showtime_id)

        return BookingListResponse(
            items=[BookingDTO.model_validate(b) for b in items],
            total=total,
            page=params.page,
            size=params.size,
        )

    if status_filter:
        items = await service.booking_repo.get_by_status(
            status_filter, skip=params.offset, limit=params.size,
        )
        total = len(items)

        return BookingListResponse(
            items=[BookingDTO.model_validate(b) for b in items],
            total=total,
            page=params.page,
            size=params.size,
        )

    return BookingListResponse(
        items=[],
        total=0,
        page=params.page,
        size=params.size,
    )


@admin_router.patch(
    "/{booking_id}/status",
    response_model=BookingDTO,
    summary="[Admin] Cập nhật trạng thái đơn đặt vé",
)
async def admin_update_booking_status(
    booking_id: UUID,
    data: UpdateBookingStatusRequest,
    service: BookingServiceDep,
):
    updated = await service.booking_repo.update_status(
        booking_id, data.status,
    )

    if updated is None:
        raise BookingNotFoundError(booking_id=booking_id)

    return BookingDTO.model_validate(updated)
