from uuid import UUID
from app.shared.exceptions import BadRequestError, ConflictError


class SeatAlreadyBookedError(ConflictError):
    """Ghế đã được đặt cho suất chiếu này."""
    
    error_code = "SEAT_ALREADY_BOOKED"
    
    def __init__(self, seat_id: UUID, showtime_id: UUID) -> None:
        self.seat_id = seat_id
        self.showtime_id = showtime_id
        
        super().__init__(
            message="Ghế đã được đặt cho suất chiếu này",
            details={
                "seat_id": str(seat_id),
                "showtime_id": str(showtime_id)
            }
        )


class SeatLockedError(ConflictError):
    """Ghế đang bị khóa bởi người dùng khác."""
    
    error_code = "SEAT_LOCKED"
    
    def __init__(
        self,
        seat_id: UUID,
        showtime_id: UUID,
        locked_by: UUID | None = None
    ) -> None:
        self.seat_id = seat_id
        self.showtime_id = showtime_id
        self.locked_by = locked_by
        
        details: dict[str, str] = {
            "seat_id": str(seat_id),
            "showtime_id": str(showtime_id)
        }
        if locked_by:
            details["locked_by"] = str(locked_by)
        
        super().__init__(
            message="Ghế đang được người khác giữ chỗ",
            details=details
        )


class SeatsNotAvailableError(BadRequestError):
    """Một hoặc nhiều ghế không khả dụng."""
    
    error_code = "SEATS_NOT_AVAILABLE"
    
    def __init__(self, seat_ids: list[UUID], showtime_id: UUID) -> None:
        self.seat_ids = seat_ids
        self.showtime_id = showtime_id
        
        super().__init__(
            message="Một hoặc nhiều ghế không khả dụng",
            details={
                "seat_ids": [str(seat_id) for seat_id in seat_ids],
                "showtime_id": str(showtime_id)
            }
        )


class InvalidSeatSelectionError(BadRequestError):
    """Lựa chọn ghế không hợp lệ."""
    
    error_code = "INVALID_SEAT_SELECTION"
    
    def __init__(
        self,
        seat_ids: list[UUID],
        room_id: UUID,
        reason: str | None = None
    ) -> None:
        self.seat_ids = seat_ids
        self.room_id = room_id
        self.reason = reason
        
        details: dict[str, str | list[str]] = {
            "seat_ids": [str(seat_id) for seat_id in seat_ids],
            "room_id": str(room_id)
        }
        if reason:
            details["reason"] = reason
        
        message = reason or "Ghế được chọn không thuộc phòng chiếu này"
        
        super().__init__(
            message=message,
            details=details
        )
