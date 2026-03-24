from fastapi import Depends
from app.modules.movies.repository.movie_repository import MovieRepository, MovieRepoDep
from app.modules.movies.repository.genre_repository import GenreRepoDep, GenreRepository
from app.modules.movies.repository.movie_genre_repository import MovieGenreRepository, MovieGenreRepoDep
from typing import Annotated
from datetime import date
from uuid import UUID
from app.modules.movies.schemas.domain import (
    MovieDTO,
    MovieSearchCriteria,
    MovieCreate,
    MovieUpdate,
    NowShowingMovie,
    MovieWithGenres
)
from app.modules.movies.exceptions.movie_exceptions import (
    MovieNotFoundError,
    MovieAlreadyExistsError,
    ReleaseDateRequiredError,
    EndDateBeforeReleaseDateError,
    MovieHasShowtimesError,
)

from app.modules.showtimes.schemas.api import ShowtimeResponse

from app.modules.movies.exceptions.genre_exception import GenreNotFoundError


class MovieService:
    def __init__(self, movie_repo: MovieRepository, genre_repo: GenreRepository, movie_genre_repo: MovieGenreRepository):
        self.movie_repo = movie_repo
        self.genre_repo = genre_repo
        self.movie_genre_repo = movie_genre_repo

    async def get_movie(self, movie_uuid: UUID) -> MovieDTO:
        movie = await self.movie_repo.get_by_id(movie_id=movie_uuid)

        if movie is None:
            raise MovieNotFoundError(movie_uuid)

        return MovieDTO.model_validate(movie)

    async def search_movies(self, criteria: MovieSearchCriteria, skip: int, limit: int) -> tuple[list[MovieDTO], int]:
        movies, count = await self.movie_repo.search_movies(criteria, skip, limit)

        movie_dtos = [MovieDTO.model_validate(movie) for movie in movies]

        return movie_dtos, count

    async def create_movie(self, data: MovieCreate) -> MovieDTO:
        if await self.movie_repo.exists_by_title(data.title):
            raise MovieAlreadyExistsError(data.title)

        if data.end_date and data.release_date is None:
            raise ReleaseDateRequiredError()

        if data.release_date and data.end_date and data.end_date < data.release_date:
            raise EndDateBeforeReleaseDateError(
                release_date=data.release_date,
                end_date=data.end_date
            )

        if data.genre_ids:
            genres = await self.genre_repo.get_by_ids(data.genre_ids)
            found_ids = {g.id for g in genres}
            missing = [gid for gid in data.genre_ids if gid not in found_ids]
            if missing:
                raise GenreNotFoundError(missing[0])

        movie = await self.movie_repo.create(data)

        if data.genre_ids:
            await self.movie_genre_repo.add_genres_to_movie(movie.id, data.genre_ids)

        return MovieDTO.model_validate(movie)

    async def update_movie(self, movie_id: UUID, data: MovieUpdate) -> MovieDTO:
        movie = await self.movie_repo.get_by_id(movie_id)

        if movie is None:
            raise MovieNotFoundError(movie_id)

        if data.title and data.title != movie.title:
            if await self.movie_repo.exists_by_title(data.title):
                raise MovieAlreadyExistsError(data.title)

        release_date = data.release_date if data.release_date is not None else movie.release_date
        end_date = data.end_date if data.end_date is not None else movie.end_date

        if end_date and release_date is None:
            raise ReleaseDateRequiredError()

        if release_date and end_date and end_date < release_date:
            raise EndDateBeforeReleaseDateError(
                release_date=release_date, end_date=end_date)

        updated = await self.movie_repo.update(movie=movie, movie_data=data)

        return MovieDTO.model_validate(updated)

    async def delete_movie(self, movie_id: UUID) -> None:
        movie = await self.movie_repo.get_by_id_with_showtimes(movie_id)

        if movie is None:
            raise MovieNotFoundError(movie_id)

        if movie.showtimes:
            raise MovieHasShowtimesError(movie_id, len(movie.showtimes))

        await self.movie_repo.delete(movie_id)

    async def get_now_showing(self, cinema_id: UUID | None, skip: int, limit: int) -> list[MovieDTO]:
        movies = await self.movie_repo.get_now_showing(
            cinema_id=cinema_id,
            skip=skip,
            limit=limit
        )

        return list(MovieDTO.model_validate(movie) for movie in movies)

    async def get_coming_soon(self, cinema_id: UUID | None, skip: int, limit: int = 20) -> list[MovieDTO]:
        movies = await self.movie_repo.get_coming_soon(cinema_id, skip, limit)

        return list(MovieDTO.model_validate(movie) for movie in movies)

    async def add_genres_to_movie(self, movie_id: UUID, genre_ids: list[UUID]) -> MovieWithGenres:
        movie = await self.movie_repo.get_by_id(movie_id)
        if movie is None:
            raise MovieNotFoundError(movie_id)

        if genre_ids:
            genres = await self.genre_repo.get_by_ids(genre_ids)
            found_ids = {g.id for g in genres}
            missing = [gid for gid in genre_ids if gid not in found_ids]
            if missing:
                raise GenreNotFoundError(missing[0])

            await self.movie_genre_repo.add_genres_to_movie(movie_id, genre_ids)

        movie_with_genres = await self.movie_repo.get_by_id_with_genres(movie_id)
        return MovieWithGenres.model_validate(movie_with_genres)

    async def remove_genres_from_movie(self, movie_id: UUID, genre_ids: list[UUID]) -> MovieWithGenres:
        movie = await self.movie_repo.get_by_id(movie_id)
        if movie is None:
            raise MovieNotFoundError(movie_id)

        if genre_ids:
            genres = await self.genre_repo.get_by_ids(genre_ids)
            found_ids = {g.id for g in genres}
            missing = [gid for gid in genre_ids if gid not in found_ids]
            if missing:
                raise GenreNotFoundError(missing[0])

            await self.movie_genre_repo.remove_genres_from_movie(movie_id, genre_ids)

        movie_with_genres = await self.movie_repo.get_by_id_with_genres(movie_id)
        return MovieWithGenres.model_validate(movie_with_genres)

    async def set_movie_genres(self, movie_id: UUID, genre_ids: list[UUID]) -> MovieWithGenres:
        movie = await self.movie_repo.get_by_id(movie_id)
        if movie is None:
            raise MovieNotFoundError(movie_id)

        if genre_ids:
            genres = await self.genre_repo.get_by_ids(genre_ids)
            found_ids = {g.id for g in genres}
            missing = [gid for gid in genre_ids if gid not in found_ids]
            if missing:
                raise GenreNotFoundError(missing[0])

        await self.movie_genre_repo.set_movie_genres(movie_id, genre_ids)

        movie_with_genres = await self.movie_repo.get_by_id_with_genres(movie_id)
        return MovieWithGenres.model_validate(movie_with_genres)

    async def get_movie_showtimes(
        self,
        movie_id: UUID,
        cinema_id: UUID | None = None,
        filter_date: date | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[ShowtimeResponse]:
        movie = await self.movie_repo.get_by_id(movie_id)
        if movie is None:
            raise MovieNotFoundError(movie_id)

        showtimes = await self.movie_repo.get_showtimes_for_movie(
            movie_id=movie_id,
            cinema_id=cinema_id,
            filter_date=filter_date,
            skip=skip,
            limit=limit
        )

        return [ShowtimeResponse.model_validate(s) for s in showtimes]


def get_movie_service(
    movie_repo: MovieRepoDep,
    genre_repo: GenreRepoDep,
    movie_genre_repo: MovieGenreRepoDep
) -> MovieService:
    return MovieService(movie_repo, genre_repo, movie_genre_repo)


MovieServiceDep = Annotated[MovieService, Depends(get_movie_service)]
