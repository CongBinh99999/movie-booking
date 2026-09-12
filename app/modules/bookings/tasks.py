"""Vòng lặp nền dọn booking PENDING đã quá hạn.

Không có nó, booking hết hạn vẫn nằm ở PENDING mãi mãi, mà
``get_booked_seats_for_showtime`` chỉ loại CANCELLED/EXPIRED — nghĩa là ghế
của những booking đó không bao giờ được trả lại.
"""
import asyncio
import logging

from app.modules.bookings.repository.booking_repository import BookingRepository
from app.modules.bookings.repository.booking_seat_repository import BookingSeatRepository
from app.modules.bookings.service.booking_service import BookingService
from app.modules.cinemas.repository.seat_repository import SeatRepository
from app.modules.showtimes.repository import ShowtimeRepository
from app.shared.database import AsyncSessionLocal
from app.shared.redis import get_redis_client

logger = logging.getLogger(__name__)

EXPIRE_INTERVAL_SECONDS = 60
LOCK_KEY = "lock:expire-bookings"


async def expire_bookings_once() -> int:
    """Chạy một lượt dọn. Trả về số booking đã chuyển sang EXPIRED."""
    async with AsyncSessionLocal() as session, get_redis_client() as redis:
        # ponytail: khoá Redis để nhiều uvicorn worker không cùng dọn một lượt.
        # Đủ dùng cho scheduler in-process; cần retry/observability thì chuyển
        # sang Celery beat.
        acquired = await redis.set(
            LOCK_KEY, "1", nx=True, ex=EXPIRE_INTERVAL_SECONDS
        )
        if not acquired:
            return 0

        service = BookingService(
            booking_repo=BookingRepository(session),
            booking_seat_repo=BookingSeatRepository(session),
            showtime_repo=ShowtimeRepository(session),
            seat_repo=SeatRepository(session),
            redis=redis,
        )
        count = await service.expire_pending_bookings()
        await session.commit()
        return count


async def expire_bookings_loop() -> None:
    """Chạy ``expire_bookings_once`` mỗi phút cho tới khi bị cancel."""
    while True:
        try:
            count = await expire_bookings_once()
            if count:
                logger.info("Đã hết hạn %d booking", count)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Một lượt lỗi không được giết cả vòng lặp.
            logger.exception("Lỗi khi dọn booking hết hạn")

        await asyncio.sleep(EXPIRE_INTERVAL_SECONDS)
