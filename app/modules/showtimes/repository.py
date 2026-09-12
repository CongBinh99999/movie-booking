"""Showtime repository - data access layer for Showtime entity."""
from fastapi import Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlmodel import col
from datetime import datetime, time, timedelta, timezone, date

from app.shared.dependencies import DbSession
from app.modules.showtimes.models import Showtimes
from app.modules.showtimes.schemas.domain import ShowtimeCreate, ShowtimeUpdate
from app.modules.cinemas.models import Rooms


class ShowtimeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD cơ bản ──────────────────────────────────────────

    # ── Filter dùng chung cho get_* và count_* ───────────────

    @staticmethod
    def _day_bounds(start_date: date, end_date: date | None = None):
        """Nửa khoảng [đầu ngày start_date, đầu ngày sau end_date)."""
        last = end_date if end_date is not None else start_date
        return (
            datetime.combine(start_date, time.min, tzinfo=timezone.utc),
            datetime.combine(last + timedelta(days=1), time.min, tzinfo=timezone.utc),
        )

    @classmethod
    def _cinema_conditions(cls, cinema_id: UUID, filter_date: date | None):
        conditions = [Rooms.cinema_id == cinema_id]
        if filter_date is not None:
            day_start, day_end = cls._day_bounds(filter_date)
            conditions += [
                Showtimes.start_time >= day_start,
                Showtimes.start_time < day_end,
            ]
        return conditions

    async def get_by_id(self, showtime_id: UUID) -> Showtimes | None:
        result = await self.db.execute(
            select(Showtimes)
            .where(Showtimes.id == showtime_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Showtimes]:
        result = await self.db.execute(
            select(Showtimes)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def create(self, data: ShowtimeCreate) -> Showtimes:
        showtime = Showtimes(
            movie_id=data.movie_id,
            room_id=data.room_id,
            start_time=data.start_time,
            end_time=data.end_time,
            base_price=data.base_price
        )

        self.db.add(showtime)
        await self.db.flush()
        await self.db.refresh(showtime)

        return showtime

    async def update(self, showtime: Showtimes, data: ShowtimeUpdate) -> Showtimes:
        updated_data = data.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(showtime, key, value)

        await self.db.flush()
        await self.db.refresh(showtime)

        return showtime

    async def delete(self, showtime: Showtimes) -> None:
        await self.db.delete(showtime)
        await self.db.flush()

    async def count_bookings(self, showtime_id: UUID) -> int:
        """Đếm booking của suất chiếu (dùng count query, không lazy load)."""
        from app.modules.bookings.models import Bookings
        result = await self.db.execute(
            select(func.count(Bookings.id))
            .where(Bookings.showtime_id == showtime_id)
        )
        return result.scalar_one()

    # ── Query methods ────────────────────────────────────────

    async def get_by_movie(self, movie_id: UUID, skip: int = 0, limit: int = 100) -> list[Showtimes]:
        result = await self.db.execute(
            select(Showtimes)
            .where(Showtimes.movie_id == movie_id)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_room(self, room_id: UUID, skip: int = 0, limit: int = 100) -> list[Showtimes]:
        result = await self.db.execute(
            select(Showtimes)
            .where(Showtimes.room_id == room_id)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_cinema(
        self, cinema_id: UUID, filter_date: date | None = None,
        skip: int = 0, limit: int = 100
    ) -> list[Showtimes]:
        query = (
            select(Showtimes)
            .join(Rooms, Showtimes.room_id == Rooms.id)
            .where(*self._cinema_conditions(cinema_id, filter_date))
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_date(self, target_date: date, skip: int = 0, limit: int = 100) -> list[Showtimes]:
        day_start = datetime.combine(
            target_date, time.min, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        result = await self.db.execute(
            select(Showtimes)
            .where(Showtimes.start_time >= day_start)
            .where(Showtimes.start_time < day_end)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_date_range(
        self, start_date: date, end_date: date,
        skip: int = 0, limit: int = 100
    ) -> list[Showtimes]:
        day_start, day_end = self._day_bounds(start_date, end_date)

        result = await self.db.execute(
            select(Showtimes)
            .where(
                Showtimes.start_time >= day_start,
                Showtimes.start_time < day_end
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[Showtimes]:
        result = await self.db.execute(
            select(Showtimes)
            .where(col(Showtimes.is_active).is_(True))
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_upcoming(self, from_time: datetime | None = None, limit: int = 50) -> list[Showtimes]:
        if from_time is None:
            from_time = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(Showtimes)
            .where(col(Showtimes.start_time) > from_time)
            .order_by(Showtimes.start_time)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def count_by_movie(self, movie_id: UUID) -> int:
        """Đếm số suất chiếu của một phim."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Showtimes)
            .where(Showtimes.movie_id == movie_id)
        )

        return result.scalar_one()

    async def count_by_room(self, room_id: UUID) -> int:
        """Đếm số suất chiếu trong một phòng."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Showtimes)
            .where(Showtimes.room_id == room_id)
        )

        return result.scalar_one()

    async def count_all(self) -> int:
        """Đếm toàn bộ suất chiếu."""
        result = await self.db.execute(select(func.count()).select_from(Showtimes))

        return result.scalar_one()

    async def count_by_cinema(
        self, cinema_id: UUID, filter_date: date | None = None
    ) -> int:
        """Đếm suất chiếu của một rạp, cùng bộ lọc với get_by_cinema."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Showtimes)
            .join(Rooms, Showtimes.room_id == Rooms.id)
            .where(*self._cinema_conditions(cinema_id, filter_date))
        )

        return result.scalar_one()

    async def count_by_date_range(self, start_date: date, end_date: date) -> int:
        """Đếm suất chiếu trong khoảng ngày, cùng bộ lọc với get_by_date_range."""
        day_start, day_end = self._day_bounds(start_date, end_date)
        result = await self.db.execute(
            select(func.count())
            .select_from(Showtimes)
            .where(
                Showtimes.start_time >= day_start,
                Showtimes.start_time < day_end
            )
        )

        return result.scalar_one()

    async def count_active(self) -> int:
        """Đếm suất chiếu đang hoạt động."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Showtimes)
            .where(col(Showtimes.is_active).is_(True))
        )

        return result.scalar_one()

    # ── Status ───────────────────────────────────────────────

    async def activate(self, showtime_id: UUID) -> Showtimes | None:
        """Kích hoạt suất chiếu."""
        showtime = await self.get_by_id(showtime_id)

        if showtime is None:
            return None

        showtime.is_active = True
        await self.db.flush()
        await self.db.refresh(showtime)

        return showtime

    async def deactivate(self, showtime_id: UUID) -> Showtimes | None:
        """Vô hiệu hoá suất chiếu."""
        showtime = await self.get_by_id(showtime_id)

        if showtime is None:
            return None

        showtime.is_active = False
        await self.db.flush()
        await self.db.refresh(showtime)

        return showtime

    # ── Validation helpers ───────────────────────────────────

    async def check_room_conflict(
        self,
        room_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_id: UUID | None = None
    ) -> bool:
        """Kiểm tra xung đột lịch chiếu trong phòng.

        Hai suất chiếu xung đột khi khoảng thời gian overlap:
        existing.start_time < new.end_time AND existing.end_time > new.start_time

        Returns:
            True nếu có xung đột, False nếu không.
        """
        query = (
            select(func.count())
            .select_from(Showtimes)
            .where(
                Showtimes.room_id == room_id,
                Showtimes.start_time < end_time,
                Showtimes.end_time > start_time,
                col(Showtimes.is_active).is_(True)
            )
        )

        # Loại trừ showtime đang update (nếu có)
        if exclude_id is not None:
            query = query.where(Showtimes.id != exclude_id)

        result = await self.db.execute(query)

        return result.scalar_one() > 0

    async def get_overlapping_showtimes(
        self,
        room_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_id: UUID | None = None
    ) -> list[Showtimes]:
        """Lấy danh sách suất chiếu bị overlap trong phòng."""
        query = (
            select(Showtimes)
            .where(
                Showtimes.room_id == room_id,
                Showtimes.start_time < end_time,
                Showtimes.end_time > start_time,
                col(Showtimes.is_active).is_(True)
            )
            .order_by(Showtimes.start_time)
        )

        if exclude_id is not None:
            query = query.where(Showtimes.id != exclude_id)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    # ── With relationships (eager loading) ───────────────────

    async def get_by_id_with_movie(self, showtime_id: UUID) -> Showtimes | None:
        """Lấy suất chiếu kèm thông tin phim."""
        result = await self.db.execute(
            select(Showtimes)
            .options(selectinload(Showtimes.movie))
            .where(Showtimes.id == showtime_id)
        )

        return result.scalar_one_or_none()

    async def get_by_id_with_room(self, showtime_id: UUID) -> Showtimes | None:
        """Lấy suất chiếu kèm thông tin phòng chiếu."""
        result = await self.db.execute(
            select(Showtimes)
            .options(selectinload(Showtimes.room))
            .where(Showtimes.id == showtime_id)
        )

        return result.scalar_one_or_none()

    async def get_by_id_full(self, showtime_id: UUID) -> Showtimes | None:
        """Lấy suất chiếu kèm đầy đủ: movie, room, room.cinema."""
        result = await self.db.execute(
            select(Showtimes)
            .options(
                selectinload(Showtimes.movie),
                selectinload(Showtimes.room)
                .selectinload(Rooms.cinema)
            )
            .where(Showtimes.id == showtime_id)
        )

        return result.scalar_one_or_none()


def get_showtime_repository(
    db: DbSession
) -> ShowtimeRepository:
    return ShowtimeRepository(db)


ShowtimeRepoDep = Annotated[ShowtimeRepository,
                            Depends(get_showtime_repository)]
