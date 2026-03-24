
from fastapi import Depends
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlmodel import col, select, and_, or_, func, update
from sqlalchemy.orm import selectinload
from app.modules.movies.schemas.domain import MovieCreate, MovieUpdate, MovieSearchCriteria

from app.shared.dependencies import DbSession
from app.modules.movies.models import Movies, MovieGenres
from app.modules.cinemas.models import Rooms, Cinemas


def _get_showtimes_model():
    """Lazy import để tránh circular dependency: showtimes.service → movie_repository → Showtimes."""
    from app.modules.showtimes.models import Showtimes
    return Showtimes


class MovieRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, movie_id: UUID) -> Movies | None:
        result = await self.db.execute(
            select(Movies)
            .where(Movies.id == movie_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Movies]:
        result = await self.db.execute(
            select(Movies)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def create(self, movie_data: MovieCreate) -> Movies:
        movie = Movies(
            title=movie_data.title,
            original_title=movie_data.original_title,
            description=movie_data.description,
            duration_minutes=movie_data.duration_minutes,
            release_date=movie_data.release_date,
            end_date=movie_data.end_date,
            poster_url=movie_data.poster_url,
            trailer_url=movie_data.trailer_url,
            director=movie_data.director,
            cast_members=movie_data.cast_members,
            language=movie_data.language,
            subtitle=movie_data.subtitle,
            age_rating=movie_data.age_rating
        )
        self.db.add(movie)

        await self.db.flush()
        await self.db.refresh(movie)

        return movie

    async def update(self, movie: Movies, movie_data: MovieUpdate) -> Movies:
        data = movie_data.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(movie, key, value)

        await self.db.flush()
        await self.db.refresh(movie)

        return movie

    async def delete(self, movie_id: UUID) -> bool:
        movie = await self.get_by_id(movie_id=movie_id)
        if movie is None:
            return False

        await self.db.delete(movie)
        await self.db.flush()

        return True

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[Movies]:
        result = await self.db.execute(
            select(Movies)
            .where(col(Movies.is_active).is_(True))
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_now_showing(self, cinema_id: UUID | None = None,  skip: int = 0, limit: int = 50) -> list[Movies]:
        today = date.today()

        query = (
            select(Movies)
            .where(
                and_(
                    col(Movies.is_active).is_(True),
                    col(Movies.release_date) <= today,
                    or_(
                        col(Movies.end_date).is_(None),
                        col(Movies.end_date) >= today
                    )
                )
            )
        )
        if cinema_id:
            Showtimes = _get_showtimes_model()
            query = (
                query
                .join(Showtimes, Showtimes.movie_id == Movies.id)
                .join(Rooms, Showtimes.room_id == Rooms.id)
                .join(Cinemas, Rooms.cinema_id == Cinemas.id)
                .where(Cinemas.id == cinema_id)
                .distinct()
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_coming_soon(self, cinema_id: UUID | None = None, skip: int = 0, limit: int = 50) -> list[Movies]:
        today = date.today()

        query = (
            select(Movies)
            .where(
                and_(
                    col(Movies.is_active).is_(True),
                    col(Movies.release_date) > today
                )
            )
            .offset(skip)
            .limit(limit)
        )

        if cinema_id:
            Showtimes = _get_showtimes_model()
            query = (
                query
                .join(Showtimes, Showtimes.movie_id == Movies.id)
                .join(Rooms, Showtimes.room_id == Rooms.id)
                .join(Cinemas, Rooms.cinema_id == Cinemas.id)
                .where(Cinemas.id == cinema_id)
                .distinct()
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_genre(self, genre_id: UUID, skip: int = 0, limit: int = 50) -> list[Movies]:
        result = await self.db.execute(
            select(Movies)
            .join(MovieGenres, Movies.id == MovieGenres.movie_id)
            .where(MovieGenres.genre_id == genre_id)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Movies)
        )

        count = result.scalar()

        if count is None:
            return 0

        return count

    async def _update_active_status(self, movie_id: UUID, status: bool) -> Movies | None:
        query = (
            update(Movies)
            .where(Movies.id == movie_id)
            .values(is_active=status)
            .returning(Movies)
        )
        result = await self.db.execute(query)

        return result.scalars().one_or_none()

    async def activate(self, movie_id: UUID) -> Movies | None:
        return await self._update_active_status(movie_id, True)

    async def deactivate(self, movie_id: UUID) -> Movies | None:
        return await self._update_active_status(movie_id, False)

    async def get_by_id_with_genres(self, movie_id: UUID) -> Movies | None:
        result = await self.db.execute(
            select(Movies)
            .options(selectinload(Movies.genres))
            .where(Movies.id == movie_id)
        )

        return result.scalar_one_or_none()

    async def get_by_id_with_showtimes(
        self,
        movie_id: UUID,
        cinema_id: UUID | None = None
    ) -> Movies | None:

        query = (
            select(Movies)
            .where(Movies.id == movie_id)
            .options(
                selectinload(Movies.showtimes)
                .selectinload(_get_showtimes_model().room)
                .selectinload(Rooms.cinema)
            )
        )

        result = await self.db.execute(query)
        movie = result.scalar_one_or_none()

        if not movie:
            return None

        if cinema_id:
            movie.showtimes = [
                showtime for showtime in movie.showtimes
                if showtime.room.cinema_id == cinema_id
            ]

        return movie

    async def exists_by_title(self, title: str) -> bool:
        result = await self.db.execute(
            select(Movies)
            .where(func.lower(Movies.title) == func.lower(title))
            .limit(1)
        )

        return result.scalar_one_or_none() is not None

    def _apply_search_criteria(self, query, criteria: MovieSearchCriteria):
        if criteria.title:
            search_term = criteria.title.strip().replace("%", "\\%").replace("_", "\\_")
            query = query.where(col(Movies.title).ilike(f"%{search_term}%"))

        if criteria.original_title:
            search_term = criteria.original_title.strip().replace(
                "%", "\\%").replace("_", "\\_")
            query = query.where(
                col(Movies.original_title).ilike(f"%{search_term}%"))

        if criteria.release_date:
            query = query.where(Movies.release_date == criteria.release_date)

        if criteria.is_active is not None:
            query = query.where(Movies.is_active == criteria.is_active)

        if criteria.genre_ids:
            query = query.join(MovieGenres, Movies.id == MovieGenres.movie_id)
            query = query.where(
                col(MovieGenres.genre_id).in_(criteria.genre_ids))

        return query.distinct()

    async def search_movies(self, criteria: MovieSearchCriteria, skip: int = 0, limit: int = 50) -> tuple[list[Movies], int]:
        query = select(Movies).offset(skip).limit(limit)
        query = self._apply_search_criteria(query, criteria)

        count_query = select(func.count(
            func.distinct(Movies.id))).select_from(Movies)
        count_query = self._apply_search_criteria(count_query, criteria)

        result = await self.db.execute(query)
        movies = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar_one()

        return movies, total_count

    async def get_showtimes_for_movie(
            self, movie_id: UUID,
            cinema_id: UUID | None = None,
            filter_date: date | None = None,
            skip: int = 0,
            limit: int = 100
    ) -> list:
        Showtimes = _get_showtimes_model()
        query = (
            select(Showtimes)
            .where(Showtimes.movie_id == movie_id)
            .options(
                selectinload(Showtimes.movie),
                selectinload(Showtimes.room).selectinload(Rooms.cinema)
            )
            .order_by(Showtimes.start_time)
        )

        if cinema_id:
            query = (
                query
                .join(Rooms, Showtimes.room_id == Rooms.id)
                .where(Rooms.cinema_id == cinema_id)
            )

        if filter_date:
            query = query.where(func.date(Showtimes.start_time) == filter_date)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_movie_repo(
    db: DbSession
) -> MovieRepository:
    return MovieRepository(db)


MovieRepoDep = Annotated[MovieRepository, Depends(get_movie_repo)]
