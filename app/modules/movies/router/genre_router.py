from fastapi import APIRouter, status
from uuid import UUID
from app.modules.auth.dependencies import RequireAdmin
from app.modules.movies.schemas.api import (
    GenreCreateRequest,
    GenreListResponse,
    GenreResponse,
    MovieListResponse,
    GenreUpdateRequest,
    MovieResponse

)
from app.modules.movies.schemas.domain import GenreCreate, GenreUpdate
from app.modules.movies.service.genre_service import GenreServiceDep

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get(
    "",
    response_model=GenreListResponse,
    summary="danh sách thể loại"
)
async def get_genres(
    service: GenreServiceDep,
    skip: int = 0,
    limit: int = 20
):
    genres = await service.get_genres()
    items = [GenreResponse.model_validate(g) for g in genres]

    paginated_items = items[skip:skip + limit] if limit > 0 else items

    return GenreListResponse(items=paginated_items, total=len(items), page=(skip // limit) + 1 if limit > 0 else 1, size=limit)


@router.get(
    "/{genre_id}",
    response_model=GenreResponse,
    summary="thông tin thể loại cụ thể"
)
async def get_genre(
    genre_id: UUID,
    service: GenreServiceDep
):
    genre = await service.get_genre(genre_id)

    return GenreResponse.model_validate(genre)


@router.get(
    "/{genre_id}/movies",
    response_model=MovieListResponse,
    summary="Danh sách phim theo thể loại"
)
async def get_movies_for_genre(
    genre_id: UUID,
    service: GenreServiceDep,
    skip: int = 0,
    limit: int = 20
):
    movies, total = await service.get_movies_for_genre(genre_id, skip, limit)

    items = [MovieResponse.model_validate(m) for m in movies]

    return MovieListResponse(items=items, total=total, page=1, size=limit)


@router.post(
    "",
    response_model=GenreResponse,
    dependencies=[RequireAdmin],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo thể loại mới"
)
async def create_genre(
    data: GenreCreateRequest,
    service: GenreServiceDep
):
    genre_data = GenreCreate(**data.model_dump())
    genre = await service.create_genre(genre_data)

    return GenreResponse.model_validate(genre)


@router.put(
    "/{genre_id}",
    response_model=GenreResponse,
    dependencies=[RequireAdmin],
    summary="Cập nhật thể loại phim"
)
async def update_genre(
    genre_id: UUID,
    data: GenreUpdateRequest,
    service: GenreServiceDep
):
    updated_data = GenreUpdate(**data.model_dump())
    genre = await service.update_genre(genre_id, updated_data)

    return GenreResponse.model_validate(genre)


@router.delete(
    "/{genre_id}",
    dependencies=[RequireAdmin],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa thể loại"
)
async def delete_genre(
    genre_id: UUID,
    service: GenreServiceDep
):
    return await service.delete_genre(genre_id)
