from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone

from pydantic import Field, computed_field

from app.shared.schemas.base import BaseSchema
from app.shared.schemas.nested import (
    SeatBasic,
    RoomBasic,
    MovieBasic,
    CinemaBasic,
    ShowtimeBasic,
    BookingBasic
)
from app.modules.bookings.models import BookingStatus


class CreateBookingInput(BaseSchema):
    user_id: UUID
    showtime_id: UUID
    seat_ids: list[UUID]


class BookingSeatInput(BaseSchema):
    booking_id: UUID
    seat_id: UUID
    price: Decimal


class BookingStatusUpdate(BaseSchema):
    booking_id: UUID
    new_status: BookingStatus
    cancellation_reason: str | None = None


class SeatWithPrice(SeatBasic):
    base_price: Decimal
    price_multiplier: Decimal
    final_price: Decimal


class BookingCalculation(BaseSchema):
    seats: list[SeatWithPrice]
    total_amount: Decimal


class BookingDTO(BaseSchema):
    id: UUID
    user_id: UUID
    showtime_id: UUID
    booking_code: str
    status: BookingStatus
    total_amount: Decimal
    expires_at: datetime
    confirmed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class ShowtimeDetail(ShowtimeBasic):
    base_price: Decimal
    room: RoomBasic
    cinema: CinemaBasic


class BookingWithDetails(BaseSchema):
    id: UUID
    booking_code: str
    status: BookingStatus
    total_amount: Decimal
    expires_at: datetime
    confirmed_at: datetime | None = None
    created_at: datetime

    # Nested details
    showtime: ShowtimeDetail
    movie: MovieBasic
    seats: list[SeatWithPrice]

    @computed_field
    @property
    def is_expired(self) -> bool:
        """Booking đã hết hạn chưa."""
        return datetime.now(timezone.utc) > self.expires_at

    @computed_field
    @property
    def is_cancellable(self) -> bool:
        """Có thể hủy không."""
        return self.status == BookingStatus.PENDING and not self.is_expired

    @computed_field
    @property
    def seats_count(self) -> int:
        """Số ghế đã book."""
        return len(self.seats)


class BookingSearchCriteria(BaseSchema):
    status: BookingStatus | None = None
    user_id: UUID | None = None
    showtime_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class UserBookingHistory(BaseSchema):
    user_id: UUID
    username: str
    email: str
    phone: str | None = None
    bookings: list[BookingBasic]

    @computed_field
    @property
    def total_bookings(self) -> int:
        """Tổng số booking."""
        return len(self.bookings)

    @computed_field
    @property
    def total_spent(self) -> Decimal:
        """Tổng số tiền đã chi."""
        total = Decimal("0")
        for booking in self.bookings:
            total += booking.total_amount
        return total


class ShowtimeBookingSummary(BaseSchema):
    showtime_id: UUID
    movie: MovieBasic
    room: RoomBasic
    start_time: datetime

    total_seats: int
    booked_seats: int
    total_revenue: Decimal

    bookings: list[BookingBasic]

    @computed_field
    @property
    def available_seats(self) -> int:
        """Số ghế còn trống."""
        return self.total_seats - self.booked_seats

    @computed_field
    @property
    def occupancy_rate(self) -> float:
        """Tỷ lệ lấp đầy (%)."""
        if self.total_seats == 0:
            return 0.0
        return round((self.booked_seats / self.total_seats) * 100, 2)
