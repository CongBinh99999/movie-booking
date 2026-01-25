"""Shared schemas package."""
from app.shared.schemas.base import (
    BaseSchema,
    BaseRequest,
    BaseResponse,
)

from app.shared.schemas.nested import (
    MovieBasic,
    CinemaBasic,
    RoomBasic,
    SeatBasic,
    ShowtimeBasic,
    UserBasic,
    BookingBasic,
)

from app.shared.schemas.pagination import (
    PaginationParams,
    PaginationResponse,
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "BaseRequest",
    "BaseResponse",
    # Nested schemas
    "MovieBasic",
    "CinemaBasic",
    "RoomBasic",
    "SeatBasic",
    "ShowtimeBasic",
    "UserBasic",
    "BookingBasic",
    # Pagination
    "PaginationParams",
    "PaginationResponse",
]
