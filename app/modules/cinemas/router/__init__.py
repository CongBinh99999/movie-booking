from .cinema_router import router as cinema_router
from .room_router import router as room_router, cinema_rooms_router
from .seat_router import router as seat_router, room_seats_router

__all__ = [
    "cinema_router",
    "room_router",
    "cinema_rooms_router",
    "seat_router",
    "room_seats_router",
]
