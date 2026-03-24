from uuid import UUID
from app.shared.exceptions import NotFoundError, ConflictError, BadRequestError


class CinemaNotFoundError(NotFoundError):
    """Không tìm thấy rạp chiếu phim."""
    
    error_code = "CINEMA_NOT_FOUND"

    def __init__(self, cinema_id: UUID | None = None) -> None:
        self.cinema_id = cinema_id
        
        super().__init__(
            message="Không tìm thấy rạp chiếu phim",
            details={"cinema_id": str(cinema_id)} if cinema_id else None
        )


class CinemaAlreadyExistsError(ConflictError):
    """Rạp chiếu phim đã tồn tại."""
    
    error_code = "CINEMA_ALREADY_EXISTS"

    def __init__(self, cinema_name: str | None = None) -> None:
        self.cinema_name = cinema_name
        
        super().__init__(
            message="Rạp chiếu phim đã tồn tại",
            details={"cinema_name": cinema_name} if cinema_name else None
        )


class CinemaHasRoomsError(BadRequestError):
    """Không thể xóa rạp đang có phòng chiếu."""
    
    error_code = "CINEMA_HAS_ROOMS"

    def __init__(self, cinema_id: UUID, room_count: int) -> None:
        self.cinema_id = cinema_id
        self.room_count = room_count
        
        super().__init__(
            message=f"Không thể xóa rạp đang có {room_count} phòng chiếu",
            details={
                "cinema_id": str(cinema_id),
                "room_count": room_count
            }
        )


class CinemaInactiveError(BadRequestError):
    """Rạp chiếu phim không hoạt động."""
    
    error_code = "CINEMA_INACTIVE"

    def __init__(self, cinema_id: UUID) -> None:
        self.cinema_id = cinema_id
        
        super().__init__(
            message="Rạp chiếu phim không hoạt động",
            details={"cinema_id": str(cinema_id)}
        )
