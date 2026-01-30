from uuid import UUID
from datetime import date

from app.shared.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
)


class MovieNotFoundError(NotFoundError):
    """Không tìm thấy phim."""
    
    error_code = "MOVIE_NOT_FOUND"

    def __init__(self, movie_id: UUID | None = None) -> None:
        self.movie_id = movie_id
        
        super().__init__(
            message="Không tìm thấy phim",
            details={"movie_id": str(movie_id)} if movie_id else None
        )


class MovieAlreadyExistsError(ConflictError):
    """Tên phim đã tồn tại."""
    
    error_code = "MOVIE_ALREADY_EXISTS"

    def __init__(self, movie_name: str | None = None) -> None:
        self.movie_name = movie_name
        
        super().__init__(
            message="Tên phim đã tồn tại",
            details={"movie_name": movie_name} if movie_name else None
        )


class ReleaseDateRequiredError(BadRequestError):
    """Ngày khởi chiếu là bắt buộc."""
    
    error_code = "RELEASE_DATE_REQUIRED"

    def __init__(self) -> None:
        super().__init__(message="Ngày khởi chiếu là bắt buộc")


class EndDateBeforeReleaseDateError(BadRequestError):
    """Ngày kết thúc trước ngày khởi chiếu."""
    
    error_code = "END_DATE_BEFORE_RELEASE_DATE"

    def __init__(self, release_date: date, end_date: date) -> None:
        self.release_date = release_date
        self.end_date = end_date
        
        super().__init__(
            message="Ngày kết thúc không thể trước ngày khởi chiếu",
            details={
                "release_date": str(release_date),
                "end_date": str(end_date)
            }
        )


class ReleaseDateTooFarFutureError(BadRequestError):
    """Ngày khởi chiếu quá xa trong tương lai."""
    
    error_code = "RELEASE_DATE_TOO_FAR_FUTURE"

    def __init__(self, release_date: date, max_allowed: date) -> None:
        self.release_date = release_date
        self.max_allowed = max_allowed
        
        super().__init__(
            message="Ngày khởi chiếu vượt quá giới hạn cho phép",
            details={
                "release_date": str(release_date),
                "max_allowed": str(max_allowed)
            }
        )


class MovieHasShowtimesError(BadRequestError):
    """Không thể xóa phim đang có suất chiếu."""
    
    error_code = "MOVIE_HAS_SHOWTIMES"

    def __init__(self, movie_id: UUID, showtime_count: int) -> None:
        self.movie_id = movie_id
        self.showtime_count = showtime_count
        
        super().__init__(
            message=f"Không thể xóa phim đang có {showtime_count} suất chiếu",
            details={
                "movie_id": str(movie_id),
                "showtime_count": showtime_count
            }
        )
