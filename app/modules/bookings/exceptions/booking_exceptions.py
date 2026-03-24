from uuid import UUID
from datetime import datetime
from app.shared.exceptions import NotFoundError, BadRequestError, ForbiddenError


class BookingNotFoundError(NotFoundError):
    """Không tìm thấy đơn đặt vé."""
    
    error_code = "BOOKING_NOT_FOUND"
    
    def __init__(
        self,
        booking_id: UUID | None = None,
        booking_code: str | None = None
    ) -> None:
        self.booking_id = booking_id
        self.booking_code = booking_code
        
        details: dict[str, str] = {}
        if booking_id:
            details["booking_id"] = str(booking_id)
        if booking_code:
            details["booking_code"] = booking_code
        
        super().__init__(
            message="Không tìm thấy đơn đặt vé",
            details=details if details else None
        )


class BookingExpiredError(BadRequestError):
    """Đơn đặt vé đã hết hạn."""
    
    error_code = "BOOKING_EXPIRED"
    
    def __init__(self, booking_id: UUID, expired_at: datetime) -> None:
        self.booking_id = booking_id
        self.expired_at = expired_at
        
        super().__init__(
            message=f"Đơn đặt vé đã hết hạn lúc {expired_at.isoformat()}",
            details={
                "booking_id": str(booking_id),
                "expired_at": expired_at.isoformat()
            }
        )


class BookingAlreadyConfirmedError(BadRequestError):
    """Đơn đặt vé đã được xác nhận."""
    
    error_code = "BOOKING_ALREADY_CONFIRMED"
    
    def __init__(self, booking_id: UUID) -> None:
        self.booking_id = booking_id
        
        super().__init__(
            message="Đơn đặt vé đã được xác nhận",
            details={"booking_id": str(booking_id)}
        )


class BookingAlreadyCancelledError(BadRequestError):
    """Đơn đặt vé đã bị hủy."""
    
    error_code = "BOOKING_ALREADY_CANCELLED"
    
    def __init__(self, booking_id: UUID) -> None:
        self.booking_id = booking_id
        
        super().__init__(
            message="Đơn đặt vé đã bị hủy",
            details={"booking_id": str(booking_id)}
        )


class BookingNotPendingError(BadRequestError):
    """Đơn đặt vé không ở trạng thái chờ xử lý."""
    
    error_code = "BOOKING_NOT_PENDING"
    
    def __init__(self, booking_id: UUID, current_status: str) -> None:
        self.booking_id = booking_id
        self.current_status = current_status
        
        super().__init__(
            message=f"Đơn đặt vé không ở trạng thái chờ xử lý (hiện tại: {current_status})",
            details={
                "booking_id": str(booking_id),
                "current_status": current_status
            }
        )


class BookingOwnershipError(ForbiddenError):
    """Không có quyền truy cập đơn đặt vé."""
    
    error_code = "BOOKING_OWNERSHIP_ERROR"
    
    def __init__(self, booking_id: UUID, user_id: UUID) -> None:
        self.booking_id = booking_id
        self.user_id = user_id
        
        super().__init__(
            message="Bạn không có quyền truy cập đơn đặt vé này",
            details={
                "booking_id": str(booking_id),
                "user_id": str(user_id)
            }
        )
