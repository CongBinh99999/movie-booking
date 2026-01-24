from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.modules.cinemas.models import SeatType
from app.modules.bookings.models import BookingStatus
from app.shared.schemas.base import BaseSchema


class MovieBasic(BaseSchema):
    id: UUID
    title: str
    poster_url: str | None = None
    duration_minutes: int


class CinemaBasic(BaseSchema):
    id: UUID
    name: str
    city: str


class RoomBasic(BaseSchema):
    id: UUID
    name: str
    room_type: str


class SeatBasic(BaseSchema):
    id: UUID
    row_label: str
    seat_number: int
    seat_type: SeatType


class ShowtimeBasic(BaseSchema):
    id: UUID
    start_time: datetime
    end_time: datetime


class UserBasic(BaseSchema):
    id: UUID
    username: str
    email: str


class BookingBasic(BaseSchema):
    id: UUID
    booking_code: str
    status: BookingStatus
    total_amount: Decimal
