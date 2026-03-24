"""Cinemas service package."""
from app.modules.cinemas.service.cinema_service import (
    CinemaService,
    CinemaServiceDep,
    get_cinema_service,
)
from app.modules.cinemas.service.room_service import (
    RoomService,
    RoomServiceDep,
    get_room_service,
)
from app.modules.cinemas.service.seat_service import (
    SeatService,
    SeatServiceDep,
    get_seat_service,
)

__all__ = [
    "CinemaService",
    "CinemaServiceDep",
    "get_cinema_service",
    "RoomService",
    "RoomServiceDep",
    "get_room_service",
    "SeatService",
    "SeatServiceDep",
    "get_seat_service",
]
