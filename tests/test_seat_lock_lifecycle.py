"""Regression test cho vòng đời khoá ghế trong BookingService."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import fakeredis.aioredis
import pytest

from app.modules.bookings.service.booking_service import BookingService
from app.modules.bookings.schemas.domain import SeatStatus
from app.modules.showtimes.exceptions import (
    ShowtimeAlreadyStartedError,
    ShowtimeNotFoundError,
)


def make_seat(room_id):
    return SimpleNamespace(
        id=uuid4(), room_id=room_id, is_active=True, row_label="A",
        seat_number=1, seat_type="standard", price_multiplier=Decimal("1.00"),
    )


def make_showtime(start_offset=timedelta(hours=2)):
    return SimpleNamespace(
        id=uuid4(), room_id=uuid4(), base_price=Decimal("100000"),
        start_time=datetime.now(timezone.utc) + start_offset,
    )


def build_service(showtime, seats, *, booked=(), create_raises=None):
    booking_repo = SimpleNamespace(
        create=_create(create_raises),
    )
    booking_seat_repo = SimpleNamespace(
        get_booked_seats_for_showtime=_async_return(list(booked)),
    )
    showtime_repo = SimpleNamespace(get_by_id=_async_return(showtime))
    seat_repo = SimpleNamespace(
        get_by_ids=_async_return(seats),
        get_by_room_type=_async_return(seats),
    )
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    return BookingService(
        booking_repo, booking_seat_repo, showtime_repo, seat_repo, redis
    ), redis


def _async_return(value):
    async def _f(*a, **k):
        return value
    return _f


def _create(exc):
    async def _f(*a, **k):
        raise exc
    return _f


@pytest.mark.asyncio
async def test_lock_duoc_tra_lai_khi_tao_booking_that_bai():
    showtime = make_showtime()
    seat = make_seat(showtime.room_id)
    service, redis = build_service(
        showtime, [seat], create_raises=RuntimeError("db down")
    )
    user_id = uuid4()

    with pytest.raises(RuntimeError):
        await service.create_booking(user_id, showtime.id, [seat.id])

    assert await service.get_locked_seats(showtime.id) == [], (
        "lock phải được trả lại, nếu không ghế treo hết TTL dù booking không tồn tại"
    )


@pytest.mark.asyncio
async def test_ghe_minh_dang_giu_khong_hien_locked_voi_chinh_minh():
    showtime = make_showtime()
    seat = make_seat(showtime.room_id)
    service, _ = build_service(showtime, [seat])
    me, nguoi_khac = uuid4(), uuid4()

    await service.acquire_seat_locks(showtime.id, [seat.id], me)

    (mine,) = await service.get_available_seats(showtime.id, user_id=me)
    (theirs,) = await service.get_available_seats(showtime.id, user_id=nguoi_khac)
    (anon,) = await service.get_available_seats(showtime.id)

    assert mine.status == SeatStatus.AVAILABLE
    assert theirs.status == SeatStatus.LOCKED
    assert anon.status == SeatStatus.LOCKED


@pytest.mark.asyncio
async def test_suat_chieu_da_bat_dau_bao_dung_loi():
    showtime = make_showtime(start_offset=timedelta(hours=-1))
    seat = make_seat(showtime.room_id)
    service, _ = build_service(showtime, [seat])

    with pytest.raises(ShowtimeAlreadyStartedError) as err:
        await service.create_booking(uuid4(), showtime.id, [seat.id])

    # trước đây trả ShowtimeNotFoundError -> client nhận 404 thay vì 400
    assert not isinstance(err.value, ShowtimeNotFoundError)
    assert err.value.status_code == 400
