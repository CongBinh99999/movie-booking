from uuid import UUID
from app.shared.exceptions import NotFoundError, ConflictError, BadRequestError


class GenreNotFoundError(NotFoundError):
    """Không tìm thấy thể loại."""
    
    error_code = "GENRE_NOT_FOUND"

    def __init__(self, genre_id: UUID | None = None) -> None:
        self.genre_id = genre_id
        
        super().__init__(
            message="Không tìm thấy thể loại",
            details={"genre_id": str(genre_id)} if genre_id else None
        )


class GenreAlreadyExistsError(ConflictError):
    """Thể loại đã tồn tại."""
    
    error_code = "GENRE_ALREADY_EXISTS"

    def __init__(self, genre_name: str | None = None) -> None:
        self.genre_name = genre_name
        
        super().__init__(
            message="Thể loại đã tồn tại",
            details={"genre_name": genre_name} if genre_name else None
        )


class GenreInactiveError(BadRequestError):
    """Thể loại không hoạt động."""
    
    error_code = "GENRE_INACTIVE"

    def __init__(self, genre_id: UUID) -> None:
        self.genre_id = genre_id
        
        super().__init__(
            message="Thể loại không hoạt động",
            details={"genre_id": str(genre_id)}
        )


class GenreHasMoviesError(BadRequestError):
    """Không thể xóa thể loại đang có phim."""
    
    error_code = "GENRE_HAS_MOVIES"

    def __init__(self, genre_id: UUID, movie_count: int) -> None:
        self.genre_id = genre_id
        self.movie_count = movie_count
        
        super().__init__(
            message=f"Không thể xóa thể loại đang có {movie_count} phim",
            details={
                "genre_id": str(genre_id),
                "movie_count": movie_count
            }
        )
