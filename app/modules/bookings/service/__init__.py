"""Booking service module.

Export BookingService và DI dependencies.
"""
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends

from app.shared.dependencies import RedisClient
from app.modules.bookings.service.booking_service import BookingService
from app.modules.bookings.repository.booking_repository import (
    BookingRepoDeps,
)
from app.modules.bookings.repository.booking_seat_repository import (
    BookingSeatRepoDeps,
)
from app.modules.showtimes.repository import ShowtimeRepoDep
from app.modules.cinemas.repository.seat_repository import SeatRepoDep


def get_booking_service(
    booking_repo: BookingRepoDeps,
    booking_seat_repo: BookingSeatRepoDeps,
    showtime_repo: ShowtimeRepoDep,
    seat_repo: SeatRepoDep,
    redis: RedisClient,
) -> BookingService:
    """Factory function để tạo BookingService (FastAPI dependency).

    Args:
        booking_repo: Repository xử lý CRUD booking.
        booking_seat_repo: Repository xử lý booking_seats.
        showtime_repo: Repository truy vấn showtime.
        seat_repo: Repository truy vấn ghế.
        redis: Redis client cho seat locking.

    Returns:
        Instance của BookingService.
    """
    return BookingService(
        booking_repo=booking_repo,
        booking_seat_repo=booking_seat_repo,
        showtime_repo=showtime_repo,
        seat_repo=seat_repo,
        redis=redis,
    )


BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]

__all__ = [
    "BookingService",
    "BookingServiceDep",
    "get_booking_service",
]
