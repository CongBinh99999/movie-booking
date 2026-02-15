"""Showtimes service - business logic cho module suất chiếu."""
from fastapi import Depends
from typing import Annotated
from uuid import UUID
from datetime import datetime, timezone

from app.modules.showtimes.repository import ShowtimeRepository, ShowtimeRepoDep
from app.modules.movies.repository.movie_repository import MovieRepository, MovieRepoDep
from app.modules.cinemas.repository.room_repository import RoomRepository, RoomRepoDep

from app.modules.showtimes.schemas.domain import (
    ShowtimeDTO,
    ShowtimeCreate,
    ShowtimeUpdate,
    ShowtimeSearchCriteria,
)
from app.modules.showtimes.schemas.api import BulkShowtimeCreateRequest

from app.modules.showtimes.exceptions import (
    ShowtimeNotFoundError,
    ShowtimeConflictError,
    ShowtimeInPastError,
    ShowtimeHasBookingsError,
    InvalidShowtimeRangeError,
)
from app.modules.movies.exceptions.movie_exceptions import MovieNotFoundError
from app.modules.cinemas.exceptions.room_exceptions import (
    RoomNotFoundError,
    RoomInactiveError,
)

from app.shared.schemas.pagination import PaginationParams


class ShowtimeService:
    """Service xử lý business logic cho Showtime."""

    def __init__(
        self,
        showtime_repo: ShowtimeRepository,
        movie_repo: MovieRepository,
        room_repo: RoomRepository,
    ):
        self.showtime_repo = showtime_repo
        self.movie_repo = movie_repo
        self.room_repo = room_repo

    async def get_showtime(self, showtime_id: UUID) -> ShowtimeDTO:
        showtime = await self.showtime_repo.get_by_id(showtime_id)

        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        return ShowtimeDTO.model_validate(showtime)

    async def get_showtimes(
        self,
        criteria: ShowtimeSearchCriteria,
        pagination: PaginationParams,
    ) -> tuple[list[ShowtimeDTO], int]:
        showtimes, total = await self._search_showtimes(criteria, pagination)

        items = [ShowtimeDTO.model_validate(s) for s in showtimes]

        return items, total

    async def create_showtime(self, data: ShowtimeCreate) -> ShowtimeDTO:
        await self._validate_showtime(data)

        showtime = await self.showtime_repo.create(data)

        return ShowtimeDTO.model_validate(showtime)

    async def update_showtime(
        self, showtime_id: UUID, data: ShowtimeUpdate
    ) -> ShowtimeDTO:
        showtime = await self.showtime_repo.get_by_id(showtime_id)

        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        new_start = data.start_time if data.start_time is not None else showtime.start_time
        new_end = data.end_time if data.end_time is not None else showtime.end_time

        if new_start >= new_end:
            raise InvalidShowtimeRangeError(new_start, new_end)

        isTimeChanged = (
            data.start_time is not None or data.end_time is not None
        )
        if isTimeChanged:
            hasConflict = await self.showtime_repo.check_room_conflict(
                room_id=showtime.room_id,
                start_time=new_start,
                end_time=new_end,
                exclude_id=showtime_id,
            )
            if hasConflict:
                raise ShowtimeConflictError(
                    room_id=showtime.room_id,
                    start_time=new_start,
                    end_time=new_end,
                )

        updated = await self.showtime_repo.update(showtime, data)

        return ShowtimeDTO.model_validate(updated)

    async def delete_showtime(self, showtime_id: UUID) -> None:
        showtime = await self.showtime_repo.get_by_id(showtime_id)

        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        if await self.showtime_repo.has_bookings(showtime_id):
            raise ShowtimeHasBookingsError(
                showtime_id=showtime_id,
                booking_count=0,
            )

        await self.showtime_repo.delete(showtime)

    async def create_showtimes_bulk(
        self, data: BulkShowtimeCreateRequest
    ) -> list[ShowtimeDTO]:
        movie = await self.movie_repo.get_by_id(data.movie_id)
        if movie is None:
            raise MovieNotFoundError(data.movie_id)

        create_items: list[ShowtimeCreate] = []
        for item in data.showtimes:
            create_data = ShowtimeCreate(
                movie_id=data.movie_id,
                room_id=item.room_id,
                start_time=item.start_time,
                end_time=item.end_time,
                base_price=item.base_price,
            )
            await self._validate_room_and_conflict(create_data)
            create_items.append(create_data)

        results: list[ShowtimeDTO] = []
        for create_data in create_items:
            showtime = await self.showtime_repo.create(create_data)
            results.append(ShowtimeDTO.model_validate(showtime))

        return results

    async def activate_showtime(self, showtime_id: UUID) -> ShowtimeDTO:
        showtime = await self.showtime_repo.activate(showtime_id)

        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        return ShowtimeDTO.model_validate(showtime)

    async def deactivate_showtime(self, showtime_id: UUID) -> ShowtimeDTO:
        showtime = await self.showtime_repo.deactivate(showtime_id)

        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        return ShowtimeDTO.model_validate(showtime)

    async def _validate_showtime(
        self,
        data: ShowtimeCreate,
        exclude_id: UUID | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        compare_start = (
            data.start_time if data.start_time.tzinfo
            else data.start_time.replace(tzinfo=timezone.utc)
        )
        if compare_start <= now:
            raise ShowtimeInPastError(data.start_time)

        movie = await self.movie_repo.get_by_id(data.movie_id)
        if movie is None:
            raise MovieNotFoundError(data.movie_id)

        await self._validate_room_and_conflict(data, exclude_id)

    async def _validate_room_and_conflict(
        self,
        data: ShowtimeCreate,
        exclude_id: UUID | None = None,
    ) -> None:
        room = await self.room_repo.get_by_id(data.room_id)
        if room is None:
            raise RoomNotFoundError(data.room_id)

        if not room.is_active:
            raise RoomInactiveError(data.room_id)

        hasConflict = await self.showtime_repo.check_room_conflict(
            room_id=data.room_id,
            start_time=data.start_time,
            end_time=data.end_time,
            exclude_id=exclude_id,
        )
        if hasConflict:
            raise ShowtimeConflictError(
                room_id=data.room_id,
                start_time=data.start_time,
                end_time=data.end_time,
            )

    async def _search_showtimes(
        self,
        criteria: ShowtimeSearchCriteria,
        pagination: PaginationParams,
    ) -> tuple[list, int]:
        skip = pagination.offset
        limit = pagination.size

        if criteria.cinema_id and not criteria.movie_id and not criteria.room_id:
            showtimes = await self.showtime_repo.get_by_cinema(
                cinema_id=criteria.cinema_id,
                filter_date=criteria.date_from.date() if criteria.date_from else None,
                skip=skip,
                limit=limit,
            )
            return showtimes, len(showtimes)

        if criteria.movie_id and not criteria.room_id and not criteria.cinema_id:
            showtimes = await self.showtime_repo.get_by_movie(
                movie_id=criteria.movie_id,
                skip=skip,
                limit=limit,
            )
            total = await self.showtime_repo.count_by_movie(criteria.movie_id)
            return showtimes, total

        if criteria.room_id and not criteria.movie_id and not criteria.cinema_id:
            showtimes = await self.showtime_repo.get_by_room(
                room_id=criteria.room_id,
                skip=skip,
                limit=limit,
            )
            total = await self.showtime_repo.count_by_room(criteria.room_id)
            return showtimes, total

        if criteria.date_from and criteria.date_to:
            showtimes = await self.showtime_repo.get_by_date_range(
                start_date=criteria.date_from.date(),
                end_date=criteria.date_to.date(),
                skip=skip,
                limit=limit,
            )
            return showtimes, len(showtimes)

        if criteria.is_active is True:
            showtimes = await self.showtime_repo.get_active(
                skip=skip,
                limit=limit,
            )
            return showtimes, len(showtimes)

        showtimes = await self.showtime_repo.get_all(
            skip=skip,
            limit=limit,
        )
        return showtimes, len(showtimes)


def get_showtime_service(
    showtime_repo: ShowtimeRepoDep,
    movie_repo: MovieRepoDep,
    room_repo: RoomRepoDep,
) -> ShowtimeService:
    return ShowtimeService(showtime_repo, movie_repo, room_repo)


ShowtimeServiceDep = Annotated[ShowtimeService, Depends(get_showtime_service)]
