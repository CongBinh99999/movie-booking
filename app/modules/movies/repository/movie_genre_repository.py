from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import DbSession
from typing import Annotated
from fastapi import Depends
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert
from ..models import MovieGenres
from sqlalchemy import select, delete, and_
from sqlmodel import col


class MovieGenreRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_genres_to_movie(self, movie_id: UUID, genre_ids: list[UUID]) -> None:
        if not genre_ids:
            return
        values = [
            {"movie_id": movie_id, "genre_id": genre_id}
            for genre_id in genre_ids
        ]

        query = (
            insert(MovieGenres)
            .values(values)
            .on_conflict_do_nothing()
        )

        await self.db.execute(query)
        await self.db.flush()

    async def remove_genres_from_movie(self, movie_id: UUID, genre_ids: list[UUID]) -> None:
        if not genre_ids:
            return

        await self.db.execute(
            delete(MovieGenres)
            .where(
                and_(
                    MovieGenres.movie_id == movie_id,
                    col(MovieGenres.genre_id).in_(genre_ids)
                )
            )
        )

        await self.db.flush()

    async def set_movie_genres(self, movie_id: UUID, genre_ids: list[UUID]) -> None:
        await self.db.execute(
            delete(MovieGenres)
            .where(MovieGenres.movie_id == movie_id)
        )

        if genre_ids:
            values = [
                {"movie_id": movie_id, "genre_id": genre_id}
                for genre_id in genre_ids
            ]

            await self.db.execute(
                insert(MovieGenres).values(values)
            )

        await self.db.flush()

    async def get_genre_ids_for_movie(self, movie_id: UUID) -> list[UUID]:
        result = await self.db.execute(
            select(MovieGenres.genre_id)
            .where(MovieGenres.movie_id == movie_id)
        )
        return list(result.scalars().all())

    async def get_movie_ids_for_genre(self, genre_id: UUID) -> list[UUID]:
        result = await self.db.execute(
            select(MovieGenres.movie_id)
            .where(MovieGenres.genre_id == genre_id)
        )
        return list(result.scalars().all())


def get_movie_genre_repository(
    db: DbSession
) -> MovieGenreRepository:
    return MovieGenreRepository(db)


MovieGenreRepoDep = Annotated[MovieGenreRepository,
                              Depends(get_movie_genre_repository)]
