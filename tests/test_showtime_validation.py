"""Regression test cho validate của ShowtimeService."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.modules.showtimes.exceptions import (
    ShowtimeConflictError,
    ShowtimeHasBookingsError,
    ShowtimeInPastError,
)
from app.modules.showtimes.schemas.api import BulkShowtimeCreateRequest, BulkShowtimeItem
from app.modules.showtimes.schemas.domain import ShowtimeCreate, ShowtimeUpdate
from app.modules.showtimes.service import ShowtimeService

NOW = datetime.now(timezone.utc)


def _ret(value):
    async def _f(*a, **k):
        return value
    return _f


def build_service(*, showtime=None, booking_count=0, conflict=False, created=None):
    showtime_repo = SimpleNamespace(
        get_by_id=_ret(showtime),
        count_bookings=_ret(booking_count),
        check_room_conflict=_ret(conflict),
        delete=_ret(True),
        update=_ret(created or showtime),
        create=_ret(created),
    )
    movie_repo = SimpleNamespace(get_by_id=_ret(SimpleNamespace(id=uuid4())))
    room_repo = SimpleNamespace(get_by_id=_ret(SimpleNamespace(id=uuid4(), is_active=True)))
    return ShowtimeService(showtime_repo, movie_repo, room_repo)


def item(room_id, start_h, end_h):
    return BulkShowtimeItem(
        room_id=room_id,
        start_time=NOW + timedelta(hours=start_h),
        end_time=NOW + timedelta(hours=end_h),
        base_price=Decimal("100000"),
    )


def test_bulk_chan_trung_gio_giua_cac_item_cung_request():
    """DB chưa có item nào nên check_room_conflict không thể phát hiện — phải kiểm chéo."""
    room = uuid4()
    items = [
        ShowtimeCreate(movie_id=uuid4(), room_id=room, base_price=Decimal("1"),
                       start_time=NOW + timedelta(hours=h1), end_time=NOW + timedelta(hours=h2))
        for h1, h2 in [(1, 3), (2, 4)]        # chồng nhau 1 tiếng
    ]
    with pytest.raises(ShowtimeConflictError):
        ShowtimeService._assert_no_internal_conflicts(items)


def test_bulk_cho_qua_khi_khac_phong_hoac_khong_chong_gio():
    room_a, room_b = uuid4(), uuid4()
    ok = [
        ShowtimeCreate(movie_id=uuid4(), room_id=r, base_price=Decimal("1"),
                       start_time=NOW + timedelta(hours=h1), end_time=NOW + timedelta(hours=h2))
        for r, h1, h2 in [(room_a, 1, 3), (room_a, 3, 5), (room_b, 1, 3)]
    ]
    ShowtimeService._assert_no_internal_conflicts(ok)   # không được ném


@pytest.mark.asyncio
async def test_bulk_that_bai_thi_khong_tao_gi_ca():
    room = uuid4()
    service = build_service()
    request = BulkShowtimeCreateRequest(
        movie_id=uuid4(), showtimes=[item(room, 1, 3), item(room, 2, 4)]
    )
    with pytest.raises(ShowtimeConflictError):
        await service.create_showtimes_bulk(request)


@pytest.mark.asyncio
async def test_khong_doi_duoc_suat_chieu_ve_qua_khu():
    showtime = SimpleNamespace(
        id=uuid4(), room_id=uuid4(),
        start_time=NOW + timedelta(hours=5), end_time=NOW + timedelta(hours=7),
    )
    service = build_service(showtime=showtime)

    with pytest.raises(ShowtimeInPastError):
        await service.update_showtime(
            showtime.id,
            ShowtimeUpdate(
                start_time=NOW - timedelta(hours=2),
                end_time=NOW - timedelta(hours=1),
            ),
        )


@pytest.mark.asyncio
async def test_loi_xoa_suat_chieu_bao_dung_so_booking():
    showtime = SimpleNamespace(id=uuid4(), room_id=uuid4())
    service = build_service(showtime=showtime, booking_count=7)

    with pytest.raises(ShowtimeHasBookingsError) as err:
        await service.delete_showtime(showtime.id)

    assert err.value.booking_count == 7        # trước đây hardcode 0
    assert "7" in err.value.message
