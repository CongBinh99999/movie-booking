"""Showtimes schemas package."""
from app.modules.showtimes.schemas.domain import (
    ShowtimeDTO,
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
