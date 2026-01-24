from app.shared.schemas.base import (
    BaseRequest,
    BaseResponse
)
from app.shared.schemas.nested import RoomBasic

from app.modules.cinemas.models import SeatType
from app.modules.cinemas.schemas.domain import SeatPattern

from pydantic import Field, computed_field
from decimal import Decimal
from uuid import UUID
from datetime import datetime


class CinemaCreateRequest(BaseRequest):
    name: str = Field(..., max_length=255)
    address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    district: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    image_url: str | None = Field(default=None, max_length=500)
    latitude: Decimal
    longitude: Decimal


class CinemaUpdateRequest(BaseRequest):
    name: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    image_url: str | None = Field(default=None, max_length=500)
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class CinemaResponse(BaseResponse):
    name: str
    address: str
    city: str
    district: str | None
    phone: str | None
    email: str | None
    description: str | None
    image_url: str | None
    latitude: Decimal
    longitude: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CinemaListResponse(CinemaResponse):
    rooms: list[RoomBasic]

    @computed_field
    @property
    def room_count(self) -> int:
        return len(self.rooms)


class RoomCreateRequest(BaseRequest):
    name: str = Field(..., max_length=100)
    room_types: str = Field(..., max_length=50)
    total_rows: int = Field(..., gt=0)
    seat_per_rows: int = Field(..., gt=0)

    patterns: list[SeatPattern] | None = Field(
        default=None,
        description="Custom patterns. Nếu không truyền sẽ dùng preset theo room_types."
    )

    use_default_only: bool = Field(
        default=False,
        description="Nếu True và không có patterns, tất cả ghế sẽ là STANDARD"
    )


class RoomUpdateRequest(BaseRequest):
    name: str | None = Field(default=None, max_length=100)
    room_types: str | None = Field(default=None, max_length=50)
    total_rows: int | None = Field(default=None, gt=0)
    seat_per_rows: int | None = Field(default=None, gt=0)


class RoomResponse(BaseResponse, RoomBasic):
    total_rows: int
    seat_per_rows: int
    total_seats: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoomListResponse(BaseResponse):
    items: list["RoomResponse"]
    total: int


class SeatCreateRequest(BaseRequest):
    row_label: str = Field(..., pattern=r'^[A-Z]$')
    seat_number: int = Field(..., gt=0)
    seat_type: SeatType = Field(default=SeatType.STANDARD)
    price_multiplier: Decimal = Field(default=Decimal(
        "1.00"), ge=1.00, le=3.00, description="Hệ số giá (1.0 = chuẩn, 1.5 = VIP)")


class SeatUpdateRequest(BaseRequest):
    seat_type: SeatType | None = None
    price_multiplier: Decimal | None = Field(default=None, ge=1.0, le=3.0)
    is_active: bool | None = None


class SeatResponse(BaseResponse):
    id: UUID
    room_id: UUID
    row_label: str
    seat_number: str
    seat_tyoe: SeatType
    price_multiplier: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def seat_label(self) -> str:
        """Nhãn ghế đầy đủ, ví dụ: 'A1', 'B12'"""
        return f"{self.row_label}{self.seat_number}"


class BulkSeatCreateRequest(BaseRequest):
    seats: list[SeatCreateRequest] = Field(..., min_length=1, max_length=1500)
