"""Showtimes schemas package."""
from app.modules.showtimes.schemas.domain import (
    ShowtimeDTO,
    ShowtimeCreate,
    ShowtimeUpdate,
    ShowtimeWithDetails,
    SeatAvailability,
    ShowtimeWithSeats,
    ShowtimeSearchCriteria,
    DailyShowtimeSchedule,
    ShowtimeConflictCheck,
)

from app.modules.showtimes.schemas.api import (
    ShowtimeCreateRequest,
    ShowtimeUpdateRequest,
    ShowtimeResponse,
    ShowtimeListResponse,
    ShowtimeQueryParams,
    BulkShowtimeItem,
    BulkShowtimeCreateRequest,
)

__all__ = [
    # Domain schemas
    "ShowtimeDTO",
    "ShowtimeCreate",
    "ShowtimeUpdate",
    "ShowtimeWithDetails",
    "SeatAvailability",
    "ShowtimeWithSeats",
    "ShowtimeSearchCriteria",
    "DailyShowtimeSchedule",
    "ShowtimeConflictCheck",
    # API schemas
    "ShowtimeCreateRequest",
    "ShowtimeUpdateRequest",
    "ShowtimeResponse",
    "ShowtimeListResponse",
    "ShowtimeQueryParams",
    "BulkShowtimeItem",
    "BulkShowtimeCreateRequest",
]
