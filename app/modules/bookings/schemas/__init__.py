"""Bookings schemas package."""
from app.modules.bookings.schemas.domain import (
    CreateBookingInput,
    BookingSeatInput,
    BookingStatusUpdate,
    SeatWithPrice,
    BookingCalculation,
    BookingDTO,
    ShowtimeDetail,
    BookingWithDetails,
    BookingSearchCriteria,
    UserBookingHistory,
    ShowtimeBookingSummary,
)

from app.modules.bookings.schemas.api import (
    BookingCreateRequest,
    BookingCancelRequest,
    BookingConfirmRequest,
    BookingResponse,
    BookingListResponse,
    AdminBookingListResponse,
    BookingQueryParams,
)

__all__ = [
    # Domain schemas
    "CreateBookingInput",
    "BookingSeatInput",
    "BookingStatusUpdate",
    "SeatWithPrice",
    "BookingCalculation",
    "BookingDTO",
    "ShowtimeDetail",
    "BookingWithDetails",
    "BookingSearchCriteria",
    "UserBookingHistory",
    "ShowtimeBookingSummary",
    # API schemas
    "BookingCreateRequest",
    "BookingCancelRequest",
    "BookingConfirmRequest",
    "BookingResponse",
    "BookingListResponse",
    "AdminBookingListResponse",
    "BookingQueryParams",
]
