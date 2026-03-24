from uuid import UUID
from decimal import Decimal
from datetime import datetime

from pydantic import Field, field_validator, model_validator, computed_field

from app.shared.schemas.base import BaseRequest, BaseResponse, BaseSchema
from app.shared.schemas.nested import (
    BookingBasic,
    SeatBasic,
    ShowtimeBasic,
    MovieBasic,
    RoomBasic,
    CinemaBasic,
)
from app.shared.schemas.pagination import PaginationResponse
from app.modules.bookings.models import BookingStatus
from app.modules.bookings.schemas.domain import (
    SeatStatus,
    SeatWithPrice,
    SeatAvailabilityInfo,
)


class BookingCreateRequest(BaseRequest):
    showtime_id: UUID = Field(..., description="ID suất chiếu")
    seat_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Danh sách ID ghế muốn đặt (1-10 ghế)"
    )

    @field_validator("seat_ids")
    @classmethod
    def validate_unique_seat_ids(cls, value: list[UUID]) -> list[UUID]:
        """Không được đặt trùng ghế trong cùng một request."""
        if len(value) != len(set(value)):
            raise ValueError("Danh sách ghế không được chứa ID trùng nhau")
        return value


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
    confirmed_at: datetime | None = None
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
    showtime_id: UUID | None = Field(
        None, description="Lọc theo suất chiếu")
    date_from: datetime | None = Field(None, description="Từ ngày")
    date_to: datetime | None = Field(None, description="Đến ngày")

    @model_validator(mode='after')
    def validate_date_range(self) -> 'BookingQueryParams':
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("date_from phải trước hoặc bằng date_to")
        return self


class ShowtimeDetailForBooking(ShowtimeBasic):
    """Thông tin suất chiếu cho booking detail."""
    base_price: Decimal
    room: RoomBasic
    cinema: CinemaBasic


class BookingDetailResponse(BaseResponse):
    """Response chi tiết booking."""
    id: UUID
    booking_code: str
    status: BookingStatus
    total_amount: Decimal
    expires_at: datetime
    confirmed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    created_at: datetime

    showtime: ShowtimeDetailForBooking
    movie: MovieBasic
    seats: list[SeatWithPrice]

    @computed_field
    @property
    def seats_count(self) -> int:
        """Số ghế đã book."""
        return len(self.seats)


class SeatAvailabilityResponse(BaseResponse):
    """Response danh sách ghế với trạng thái."""
    showtime_id: UUID
    base_price: Decimal
    seats: list[SeatAvailabilityInfo]

    @computed_field
    @property
    def total_seats(self) -> int:
        """Tổng số ghế."""
        return len(self.seats)

    @computed_field
    @property
    def available_count(self) -> int:
        """Số ghế còn trống."""
        return sum(1 for s in self.seats if s.status == SeatStatus.AVAILABLE)


class CalculateBookingRequest(BaseRequest):
    """Request tính giá booking."""
    showtime_id: UUID = Field(..., description="ID suất chiếu")
    seat_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Danh sách ID ghế muốn tính giá (1-10 ghế)"
    )

    @field_validator("seat_ids")
    @classmethod
    def validate_unique_seat_ids(cls, value: list[UUID]) -> list[UUID]:
        """Không được tính trùng ghế."""
        if len(value) != len(set(value)):
            raise ValueError("Danh sách ghế không được chứa ID trùng nhau")
        return value


class BookingCalculationResponse(BaseResponse):
    """Response kết quả tính giá."""
    seats: list[SeatWithPrice]
    total_amount: Decimal


class UpdateBookingStatusRequest(BaseRequest):
    """Request admin cập nhật trạng thái booking."""
    status: BookingStatus = Field(..., description="Trạng thái mới")
    reason: str | None = Field(
        None,
        max_length=500,
        description="Lý do thay đổi trạng thái (optional)"
    )
