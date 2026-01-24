from app.shared.schemas.base import BaseSchema
from app.shared.schemas.nested import (
    CinemaBasic,
    RoomBasic,
    SeatBasic
)

from uuid import UUID
from decimal import Decimal
from datetime import datetime


class CinemaDTO(CinemaBasic):
    address: str
    district: str | None = None
    phone: str | None = None
    email: str | None = None
    description: str | None = None
    image_url: str | None
    latitude: Decimal
    longitude: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoomDTO(RoomBasic):
    total_rows: int
    seats_per_row: int
    total_seats: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SeatDTO(SeatBasic):
    room_id: UUID
    price_multiplier: Decimal
    is_active: bool
    created_at: datetime


class SeatGenerationConfig(BaseSchema):
    pass


class SeatPattern(BaseSchema):
    pass


class RoomWithSeats(BaseSchema):
    pass


class CinemaWithRooms(BaseSchema):
    pass


class CinemaSearchCriteria(BaseSchema):
    pass


class SeatAvailabilityQuery(BaseSchema):
    pass
