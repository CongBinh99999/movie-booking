from app.shared.schemas.base import BaseSchema
from app.shared.schemas.nested import (
    CinemaBasic,
    RoomBasic,
    SeatBasic
)
from app.modules.cinemas.models import SeatType

from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import Field, computed_field, model_validator


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


class SeatPattern(BaseSchema):
    row_range: str = Field(..., pattern=r'^[A-Z](-[A-Z])?$')
    seat_type: SeatType
    price_multiplier: Decimal = Field(..., ge=1.0, le=3.0)

    @computed_field
    @property
    def row_letters(self) -> list[str]:
        """'A-C' -> ['A', 'B', 'C']"""
        if "-" in self.row_range:
            start, end = self.row_range.split("-")
            return [chr(i) for i in range(ord(start), ord(end)+1)]
        return [self.row_range]


class SeatGenerationConfig(BaseSchema):
    total_rows: int = Field(..., ge=1, le=30)
    seats_per_row: int = Field(..., ge=1, le=50)
    patterns: list[SeatPattern] = []
    default_seat_type: SeatType = SeatType.STANDARD
    default_price_multiplier: Decimal = Decimal("1.0")

    @computed_field
    @property
    def total_seats(self) -> int:
        return self.total_rows * self.seats_per_row

    @model_validator(mode="after")
    def validator_patterns(self) -> "SeatGenerationConfig":
        """Kiểm tra patterns không overlap."""
        if not self.patterns:
            return self

        max_row = chr(ord('A') + self.total_rows - 1)
        covered: set = set()

        for pattern in self.patterns:
            for letter in pattern.row_letters:
                if letter > max_row:
                    raise ValueError(
                        f"Row '{letter}' vượt quá max ({max_row})")
                if letter in covered:
                    raise ValueError(f"Row '{letter}' bị duplicate")
                covered.add(letter)

        return self


class RoomWithSeats(BaseSchema):
    cinema_id: UUID
    name: str = Field(..., max_length=100)
    room_type: str = Field(..., max_length=50)
    total_rows: int = Field(..., gt=0)
    seats_per_row: int = Field(..., gt=0)
    total_seats: int = Field(..., gt=0)
    is_active: bool = True
    seats: list[SeatDTO] = Field(
        default_factory=list,
        description="Danh sách tất cả ghế trong phòng"
    )

    @computed_field
    @property
    def active_seats_count(self) -> int:
        return sum(1 for seat in self.seats if seat.is_active)

    @computed_field
    @property
    def seats_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}

        for seat in self.seats:
            seat_type = seat.seat_type.value
            counts[seat_type] = counts.get(seat_type, 0) + 1

        return counts

    @computed_field
    @property
    def seats_by_row(self) -> dict[str, list[SeatDTO]]:
        """Nhóm ghế theo hàng."""
        grouped: dict[str, list[SeatDTO]] = {}
        for seat in self.seats:
            if seat.row_label not in grouped:
                grouped[seat.row_label] = []
            grouped[seat.row_label].append(seat)

        # Sort seats within each row
        for row in grouped:
            grouped[row].sort(key=lambda s: s.seat_number)

        return grouped


class CinemaWithRooms(BaseSchema):
    name: str = Field(..., max_length=255)
    address: str
    city: str = Field(..., max_length=100)
    district: str | None = None
    phone: str | None = None
    email: str | None = None
    description: str | None = None
    image_url: str | None = None
    latitude: Decimal
    longitude: Decimal
    is_active: bool = Field(default=True)
    rooms: list[RoomDTO] = Field(
        default_factory=list,
        description="Danh sách tất cả phòng trong rạp"
    )

    @computed_field
    @property
    def total_rooms(self) -> int:
        """Tổng số phòng."""
        return len(self.rooms)

    @computed_field
    @property
    def active_rooms_count(self) -> int:
        """Số phòng đang hoạt động."""
        return sum(1 for room in self.rooms if room.is_active)

    @computed_field
    @property
    def total_capacity(self) -> int:
        """Tổng sức chứa của tất cả phòng."""
        return sum(room.total_seats for room in self.rooms if room.is_active)


class CinemaSearchCriteria(BaseSchema):
    """Schema cho search/filter cinemas."""
    city: str | None = Field(None, description="Lọc theo thành phố")
    district: str | None = Field(None, description="Lọc theo quận/huyện")
    name_contains: str | None = Field(
        None, description="Tìm theo tên (LIKE)")
    is_active: bool | None = Field(None, description="Lọc theo trạng thái")
    lat_min: Decimal | None = Field(None, ge=-90, le=90)
    lat_max: Decimal | None = Field(None, ge=-90, le=90)
    lng_min: Decimal | None = Field(None, ge=-180, le=180)
    lng_max: Decimal | None = Field(None, ge=-180, le=180)


class SeatAvailabilityQuery(BaseSchema):
    """Schema cho query seat availability trong một showtime."""
    room_id: UUID
    showtime_id: UUID
    seat_types: list[SeatType] | None = Field(
        None,
        description="Lọc theo loại ghế"
    )
    only_available: bool = Field(
        default=True,
        description="Chỉ lấy ghế còn trống"
    )
