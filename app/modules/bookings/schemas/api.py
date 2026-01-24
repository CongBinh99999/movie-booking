from uuid import UUID
from decimal import Decimal
from datetime import datetime

from pydantic import Field, model_validator

from app.shared.schemas.base import BaseRequest, BaseResponse, BaseSchema
from app.shared.schemas.nested import BookingBasic, SeatBasic, ShowtimeBasic
from app.shared.schemas.pagination import PaginationResponse
from app.modules.bookings.models import BookingStatus


class BookingCreateRequest(BaseRequest):
    showtime_id: UUID = Field(..., description="ID suất chiếu")
    seat_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Danh sách ID ghế muốn đặt (1-10 ghế)"
    )


class BookingCancelRequest(BaseRequest):
    cancellation_reason: str | None = Field(
        None,
        max_length=500,
        description="Lý do hủy (optional)"
    )


class BookingConfirmRequest(BaseRequest):
    payment_id: UUID | None = Field(
        None,
        description="ID payment (optional nếu confirm không cần payment)"
    )


class BookingResponse(BaseResponse):
    id: UUID
    booking_code: str
    status: BookingStatus
    total_amount: Decimal
    expires_at: datetime
    created_at: datetime
    showtime: ShowtimeBasic
    seats: list[SeatBasic]


class BookingListResponse(PaginationResponse[BookingBasic]):
    pass


class AdminBookingListResponse(PaginationResponse[BookingBasic]):
    pass


class BookingQueryParams(BaseSchema):
    status: BookingStatus | None = Field(None, description="Lọc theo status")
    user_id: UUID | None = Field(
        None, description="Lọc theo user (admin only)")
    date_from: datetime | None = Field(None, description="Từ ngày")
    date_to: datetime | None = Field(None, description="Đến ngày")

    @model_validator(mode='after')
    def validate_date_range(self) -> 'BookingQueryParams':
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("date_from phải trước hoặc bằng date_to")
        return self
