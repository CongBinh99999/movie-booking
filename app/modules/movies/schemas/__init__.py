"""Movies schemas package."""
from app.modules.movies.schemas.domain import (
    GenreDTO,
    MovieDTO,
    MovieWithGenres,
    MovieWithShowtimes,
    NowShowingMovie,
    ComingSoonMovie,
    MovieSearchCriteria,
)

from app.modules.movies.schemas.api import (
    MovieCreateRequest,
    MovieUpdateRequest,
    MovieResponse,
    MovieListResponse,
    GenreCreateRequest,
    GenreResponse,
    GenreListResponse,
    MovieQueryParams,
    UpdateMovieGenresRequest,
)

__all__ = [
    # Domain schemas
    "GenreDTO",
    "MovieDTO",
    "MovieWithGenres",
    "MovieWithShowtimes",
    "NowShowingMovie",
    "ComingSoonMovie",
    "MovieSearchCriteria",
    # API schemas
    "MovieCreateRequest",
    "MovieUpdateRequest",
    "MovieResponse",
    "MovieListResponse",
    "GenreCreateRequest",
    "GenreResponse",
    "GenreListResponse",
    "MovieQueryParams",
    "UpdateMovieGenresRequest",
]
