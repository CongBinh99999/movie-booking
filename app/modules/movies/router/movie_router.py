from fastapi import APIRouter
from fastapi import APIRouter, Depends, status
from uuid import UUID
from datetime import date
from app.modules.movies.service.movie_service import MovieServiceDep
from app.modules.movies.schemas.api import (
    MovieCreateRequest,
    MovieUpdateRequest,
    MovieResponse,
    MovieListResponse,
    MovieQueryParams,
    UpdateMovieGenresRequest
)
from app.modules.movies.schemas.domain import (
    MovieCreate,
    MovieUpdate,
    MovieSearchCriteria,
    MovieWithGenres,
)

from app.modules.showtimes.schemas.api import ShowtimeResponse

from app.modules.auth.dependencies import RequireAdmin


router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get(
    "",
    response_model=MovieListResponse,
    summary="Lấy danh sách phim"
)
async def list_movie(
    service: MovieServiceDep,
    params: MovieQueryParams = Depends(),
):
    if params.status == "now_showing":
        items = await service.get_now_showing(
            cinema_id=None,
            skip=params.skip,
            limit=params.limit
        )
        items = [MovieResponse.model_validate(m) for m in items]
        return MovieListResponse(items=items, total=len(items), page=1, size=params.limit)

    if params.status == "coming_soon":
        items = await service.get_coming_soon(None, params.skip, params.limit)
        items = [MovieResponse.model_validate(m) for m in items]
        return MovieListResponse(items=items, total=len(items), page=1, size=params.limit)

    criteria = MovieSearchCriteria(
        title=params.title,
        original_title=params.original_title,
        release_date=params.release_date,
        genre_ids=params.genre_ids,
        is_active=params.is_active,
    )
    movies, total = await service.search_movies(criteria, params.skip, params.limit)
    items = [MovieResponse.model_validate(m) for m in movies]
    return MovieListResponse(items=items, total=total, page=1, size=params.limit)


@router.get(
    "/now-showing",
    response_model=MovieListResponse,
    summary="Danh sách phim đang chiếu"
)
async def now_showing(
    service: MovieServiceDep,
    cinema_id: UUID | None = None,
    skip: int = 0,
    limit: int = 20,
):
    movies = await service.get_now_showing(
        cinema_id=cinema_id,
        skip=skip,
        limit=limit
    )

    items = [MovieResponse.model_validate(m) for m in movies]

    return MovieListResponse(items=items, total=len(items), page=1, size=limit)


@router.get(
    "/coming-soon",
    response_model=MovieListResponse,
    summary="Danh sách các phim sắp chiếu"
)
async def coming_soon(
    service: MovieServiceDep,
    cinema_id: UUID | None = None,
    skip: int = 0,
    limit: int = 20
):
    movies = await service.get_coming_soon(
        cinema_id=cinema_id,
        skip=skip,
        limit=limit
    )

    items = [MovieResponse.model_validate(m) for m in movies]

    return MovieListResponse(items=items, total=len(items), page=1, size=limit)


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Hiển thị một phim cụ thể"
)
async def get_movie(
    movie_id: UUID,
    service: MovieServiceDep
):
    movie = await service.get_movie(movie_uuid=movie_id)

    return MovieResponse.model_validate(movie)


@router.post(
    "",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAdmin],
    summary="Tải phim lên"
)
async def create_movie(
    data: MovieCreateRequest,
    service: MovieServiceDep
):
    movie_data = MovieCreate(**data.model_dump())

    movie = await service.create_movie(movie_data)

    return MovieResponse.model_validate(movie)


@router.put(
    "/{movie_id}",
    response_model=MovieResponse,
    dependencies=[RequireAdmin],
    summary="Cập nhật thông tin phim"
)
async def update_movie(
    movie_id: UUID,
    data: MovieUpdateRequest,
    service: MovieServiceDep
):
    update_data = MovieUpdate(**data.model_dump(exclude_unset=True))

    movie = await service.update_movie(movie_id, update_data)

    return MovieResponse.model_validate(movie)


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireAdmin],
    summary="Xóa phim"
)
async def delete_movie(
    movie_id: UUID,
    service: MovieServiceDep
):
    return await service.delete_movie(movie_id)


@router.patch(
    "/{movie_id}/genres",
    response_model=MovieWithGenres,
    dependencies=[RequireAdmin]
)
async def update_movie_genres(
    movie_id: UUID,
    data: UpdateMovieGenresRequest,
    service: MovieServiceDep,
):
    if data.action == "add":
        return await service.add_genres_to_movie(movie_id, data.genre_ids)
    if data.action == "remove":
        return await service.remove_genres_from_movie(movie_id, data.genre_ids)
    if data.action == "replace":
        return await service.set_movie_genres(movie_id, data.genre_ids)


@router.get(
    "/{movie_id}/showtimes",
    response_model=list[ShowtimeResponse],
    summary="Lấy suất chiếu của phim"
)
async def get_movie_showtimes(
    movie_id: UUID,
    service: MovieServiceDep,
    cinema_id: UUID | None = None,
    filter_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
):
    return await service.get_movie_showtimes(
        movie_id=movie_id,
        cinema_id=cinema_id,
        filter_date=filter_date,
        skip=skip,
        limit=limit
    )
