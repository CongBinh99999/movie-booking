from uuid import UUID
from datetime import datetime
from app.shared.exceptions import NotFoundError, BadRequestError, ConflictError


class ShowtimeNotFoundError(NotFoundError):
    """Không tìm thấy suất chiếu."""
    
    error_code = "SHOWTIME_NOT_FOUND"
    
    def __init__(self, showtime_id: UUID | None = None) -> None:
        self.showtime_id = showtime_id
        
        details: dict[str, str] | None = None
        if showtime_id:
            details = {"showtime_id": str(showtime_id)}
        
        super().__init__(
            message="Không tìm thấy suất chiếu",
            details=details
        )


class ShowtimeConflictError(ConflictError):
    """Phòng đã có suất chiếu trong khung giờ này."""
    
    error_code = "SHOWTIME_CONFLICT"
    
    def __init__(
        self,
        room_id: UUID,
        start_time: datetime,
        end_time: datetime,
        conflicting_showtime_id: UUID | None = None
    ) -> None:
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.conflicting_showtime_id = conflicting_showtime_id
        
        details: dict[str, str] = {
            "room_id": str(room_id),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        if conflicting_showtime_id:
            details["conflicting_showtime_id"] = str(conflicting_showtime_id)
        
        super().__init__(
            message="Phòng không khả dụng trong khung giờ yêu cầu",
            details=details
        )


class ShowtimeInPastError(BadRequestError):
    """Không thể tạo suất chiếu trong quá khứ."""
    
    error_code = "SHOWTIME_IN_PAST"
    
    def __init__(self, start_time: datetime) -> None:
        self.start_time = start_time
        
        super().__init__(
            message="Không thể tạo suất chiếu trong quá khứ",
            details={"start_time": start_time.isoformat()}
        )


class ShowtimeHasBookingsError(BadRequestError):
    """Không thể xóa suất chiếu đã có đặt vé."""
    
    error_code = "SHOWTIME_HAS_BOOKINGS"
    
    def __init__(self, showtime_id: UUID, booking_count: int) -> None:
        self.showtime_id = showtime_id
        self.booking_count = booking_count
        
        super().__init__(
            message=f"Không thể xóa suất chiếu có {booking_count} đơn đặt vé",
            details={
                "showtime_id": str(showtime_id),
                "booking_count": str(booking_count)
            }
        )


class ShowtimeInactiveError(BadRequestError):
    """Suất chiếu không hoạt động."""
    
    error_code = "SHOWTIME_INACTIVE"
    
    def __init__(self, showtime_id: UUID) -> None:
        self.showtime_id = showtime_id
        
        super().__init__(
            message="Suất chiếu không hoạt động",
            details={"showtime_id": str(showtime_id)}
        )


class InvalidShowtimeRangeError(BadRequestError):
    """Thời gian kết thúc phải sau thời gian bắt đầu."""
    
    error_code = "INVALID_SHOWTIME_RANGE"
    
    def __init__(self, start_time: datetime, end_time: datetime) -> None:
        self.start_time = start_time
        self.end_time = end_time
        
        super().__init__(
            message="Thời gian kết thúc phải sau thời gian bắt đầu",
            details={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        )