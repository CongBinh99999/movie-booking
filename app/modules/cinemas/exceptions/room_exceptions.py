from uuid import UUID
from app.shared.exceptions import NotFoundError, ConflictError, BadRequestError


class RoomNotFoundError(NotFoundError):
    """Không tìm thấy phòng chiếu."""
    
    error_code = "ROOM_NOT_FOUND"

    def __init__(self, room_id: UUID | None = None) -> None:
        self.room_id = room_id
        
        super().__init__(
            message="Không tìm thấy phòng chiếu",
            details={"room_id": str(room_id)} if room_id else None
        )


class RoomAlreadyExistsError(ConflictError):
    """Phòng chiếu đã tồn tại."""
    
    error_code = "ROOM_ALREADY_EXISTS"

    def __init__(self, room_name: str | None = None) -> None:
        self.room_name = room_name
        
        super().__init__(
            message="Phòng chiếu đã tồn tại",
            details={"room_name": room_name} if room_name else None
        )


class RoomHasShowtimesError(BadRequestError):
    """Không thể xóa phòng đang có suất chiếu."""
    
    error_code = "ROOM_HAS_SHOWTIMES"

    def __init__(self, room_id: UUID, showtime_count: int) -> None:
        self.room_id = room_id
        self.showtime_count = showtime_count
        
        super().__init__(
            message=f"Không thể xóa phòng đang có {showtime_count} suất chiếu",
            details={
                "room_id": str(room_id),
                "showtime_count": showtime_count
            }
        )


class RoomInactiveError(BadRequestError):
    """Phòng chiếu không hoạt động."""
    
    error_code = "ROOM_INACTIVE"

    def __init__(self, room_id: UUID) -> None:
        self.room_id = room_id
        
        super().__init__(
            message="Phòng chiếu không hoạt động",
            details={"room_id": str(room_id)}
        )
