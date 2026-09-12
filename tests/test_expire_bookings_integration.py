"""Test tích hợp: booking hết hạn phải trả ghế lại cho suất chiếu."""
import fakeredis.aioredis
import pytest

from app.modules.bookings.models import BookingStatus
from app.modules.bookings.repository.booking_repository import BookingRepository
from app.modules.bookings.repository.booking_seat_repository import BookingSeatRepository
from app.modules.bookings.service.booking_service import BookingService
from app.modules.cinemas.repository.seat_repository import SeatRepository
from app.modules.showtimes.repository import ShowtimeRepository
from tests.factories import make_booking, make_room, make_seats, make_showtime, make_user


def build_service(session):
    return BookingService(
        BookingRepository(session), BookingSeatRepository(session),
        ShowtimeRepository(session), SeatRepository(session),
        fakeredis.aioredis.FakeRedis(decode_responses=True),
    )


@pytest.fixture
async def expired_booking(session):
    user = await make_user(session)
    _, room = await make_room(session)
    seats = await make_seats(session, room, count=2)
    _, showtime = await make_showtime(session, room)
    booking = await make_booking(
        session, user, showtime, seats, expires_in_minutes=-5   # đã quá hạn
    )
    await session.commit()
    return booking, showtime, seats


async def test_ghe_bi_chiem_khi_chua_don(session, expired_booking):
    """Trạng thái lỗi: PENDING quá hạn vẫn tính là đã đặt, ghế kẹt vĩnh viễn."""
    _, showtime, seats = expired_booking
    booked = await BookingSeatRepository(session).get_booked_seats_for_showtime(showtime.id)
    assert set(booked) == {s.id for s in seats}


async def test_don_xong_thi_ghe_duoc_tra_lai(session, expired_booking):
    booking, showtime, _ = expired_booking

    assert await build_service(session).expire_pending_bookings() == 1
    await session.commit()

    refreshed = await BookingRepository(session).get_by_id(booking.id)
    assert refreshed.status == BookingStatus.EXPIRED
    assert await BookingSeatRepository(session).get_booked_seats_for_showtime(showtime.id) == []


async def test_booking_con_han_khong_bi_dong_cham(session):
    user = await make_user(session)
    _, room = await make_room(session)
    seats = await make_seats(session, room, count=1)
    _, showtime = await make_showtime(session, room)
    booking = await make_booking(session, user, showtime, seats, expires_in_minutes=15)
    await session.commit()

    assert await build_service(session).expire_pending_bookings() == 0
    await session.commit()

    refreshed = await BookingRepository(session).get_by_id(booking.id)
    assert refreshed.status == BookingStatus.PENDING
