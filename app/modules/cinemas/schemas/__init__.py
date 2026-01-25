"""Cinemas schemas package."""
from app.modules.cinemas.schemas.domain import (
    CinemaDTO,
    RoomDTO,
    SeatDTO,
    SeatPattern,
    SeatGenerationConfig,
    RoomWithSeats,
    CinemaWithRooms,
    CinemaSearchCriteria,
    SeatAvailabilityQuery,
)

from app.modules.cinemas.schemas.api import (
    CinemaCreateRequest,
    CinemaUpdateRequest,
    CinemaResponse,
    CinemaWithRoomsResponse,
    CinemaListResponse,
    RoomCreateRequest,
    RoomUpdateRequest,
    RoomResponse,
    RoomListResponse,
    SeatCreateRequest,
    SeatUpdateRequest,
    SeatResponse,
    SeatListResponse,
    BulkSeatCreateRequest,
)

__all__ = [
    # Domain schemas
    "CinemaDTO",
    "RoomDTO",
    "SeatDTO",
    "SeatPattern",
    "SeatGenerationConfig",
    "RoomWithSeats",
    "CinemaWithRooms",
    "CinemaSearchCriteria",
    "SeatAvailabilityQuery",
    # API schemas
    "CinemaCreateRequest",
    "CinemaUpdateRequest",
    "CinemaResponse",
    "CinemaWithRoomsResponse",
    "CinemaListResponse",
    "RoomCreateRequest",
    "RoomUpdateRequest",
    "RoomResponse",
    "RoomListResponse",
    "SeatCreateRequest",
    "SeatUpdateRequest",
    "SeatResponse",
    "SeatListResponse",
    "BulkSeatCreateRequest",
]
