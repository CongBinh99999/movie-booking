"""Test tích hợp: total của phân trang phải là tổng thật, không phải cỡ trang.

PR "fix: return real total count" chỉ kiểm bằng tay vì cần DB thật. Đây là bản
tự động hoá của kiểm chứng đó.
"""
from datetime import timedelta
from decimal import Decimal

import pytest

from app.modules.cinemas.models import Cinemas, Rooms
from app.modules.movies.models import Movies
from app.modules.movies.repository.movie_repository import MovieRepository
from app.modules.showtimes.models import Showtimes
from app.modules.showtimes.repository import ShowtimeRepository
from tests.factories import now

TOTAL = 25
PAGE = 10


@pytest.fixture
async def seeded(session):
    """25 phim đang chiếu, mỗi phim một suất chiếu trong cùng một phòng."""
    today = now().date()
    cinema = Cinemas(name="CGV", address="1 Main St", city="HN")
    session.add(cinema)
    await session.flush()
    room = Rooms(cinema_id=cinema.id, name="R1", total_rows=1,
                 seats_per_row=1, total_seats=1)
    session.add(room)
    await session.flush()

    for i in range(TOTAL):
        movie = Movies(title=f"M{i}", original_title=f"M{i}", duration_minutes=90,
                       release_date=today - timedelta(days=1), is_active=True)
        session.add(movie)
        await session.flush()
        session.add(Showtimes(
            movie_id=movie.id, room_id=room.id,
            start_time=now() + timedelta(hours=i + 1),
            end_time=now() + timedelta(hours=i + 3),
            base_price=Decimal("100000"), is_active=True,
        ))
    await session.commit()
    return cinema


async def test_movies_now_showing(session, seeded):
    repo = MovieRepository(session)
    assert len(await repo.get_now_showing(skip=0, limit=PAGE)) == PAGE
    assert await repo.count_now_showing() == TOTAL


async def test_movies_now_showing_loc_theo_rap(session, seeded):
    """Join sang showtimes làm nhân bản dòng — count phải DISTINCT."""
    repo = MovieRepository(session)
    assert len(await repo.get_now_showing(cinema_id=seeded.id, skip=0, limit=PAGE)) == PAGE
    assert await repo.count_now_showing(seeded.id) == TOTAL


@pytest.mark.parametrize("getter,counter", [
    ("get_all", "count_all"),
    ("get_active", "count_active"),
])
async def test_showtimes_total(session, seeded, getter, counter):
    repo = ShowtimeRepository(session)
    assert len(await getattr(repo, getter)(skip=0, limit=PAGE)) == PAGE
    assert await getattr(repo, counter)() == TOTAL


async def test_showtimes_theo_rap_va_khoang_ngay(session, seeded):
    repo = ShowtimeRepository(session)
    today = now().date()

    assert len(await repo.get_by_cinema(seeded.id, skip=0, limit=PAGE)) == PAGE
    assert await repo.count_by_cinema(seeded.id) == TOTAL

    end = today + timedelta(days=3)
    assert len(await repo.get_by_date_range(today, end, skip=0, limit=PAGE)) == PAGE
    assert await repo.count_by_date_range(today, end) == TOTAL


async def test_trang_cuoi_khong_day(session, seeded):
    """skip=20 chỉ còn 5 bản ghi, nhưng total vẫn phải là 25."""
    repo = ShowtimeRepository(session)
    assert len(await repo.get_all(skip=20, limit=PAGE)) == TOTAL - 20
    assert await repo.count_all() == TOTAL
