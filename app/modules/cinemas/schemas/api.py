"""Cinemas API schemas.

Các schema dùng cho API endpoints trong module cinemas.
Bao gồm Request và Response schemas cho Cinema, Room, Seat.
"""
from app.shared.schemas.base import (
    BaseRequest,
    BaseResponse
)
from app.shared.schemas.nested import RoomBasic
from app.shared.schemas.pagination import PaginationResponse

from app.modules.cinemas.models import SeatType
from app.modules.cinemas.schemas.domain import SeatPattern

from pydantic import Field, computed_field
from decimal import Decimal
from uuid import UUID
from datetime import datetime


class CinemaCreateRequest(BaseRequest):
    """Request tạo rạp mới.
    
    Attributes:
        name: Tên rạp.
        address: Địa chỉ chi tiết.
        city: Thành phố.
        district: Quận/huyện (optional).
        phone: Số điện thoại (optional).
        email: Email liên hệ (optional).
        description: Mô tả về rạp (optional).
        image_url: Link ảnh rạp (optional).
        latitude: Vĩ độ (để hiển thị trên bản đồ).
        longitude: Kinh độ (để hiển thị trên bản đồ).
    """
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
    """Request cập nhật thông tin rạp.
    
    Tất cả field đều optional.
    Chỉ truyền field nào cần update.
    """
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
    """Response chi tiết một rạp.
    
    Attributes:
        id: ID duy nhất của rạp.
        name: Tên rạp.
        address: Địa chỉ.
        city: Thành phố.
        district: Quận/huyện.
        phone: Số điện thoại.
        email: Email.
        description: Mô tả.
        image_url: Link ảnh.
        latitude: Vĩ độ.
        longitude: Kinh độ.
        is_active: Rạp còn hoạt động không.
        created_at: Thời điểm tạo.
        updated_at: Thời điểm cập nhật.
    """
    id: UUID
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


class CinemaWithRoomsResponse(CinemaResponse):
    """Response rạp kèm danh sách phòng.
    
    Mở rộng từ CinemaResponse, thêm danh sách phòng chiếu.
    
    Attributes:
        rooms: Danh sách phòng chiếu.
        room_count: Số lượng phòng (computed).
    """
    rooms: list[RoomBasic] = Field(default_factory=list)

    @computed_field
    @property
    def room_count(self) -> int:
        """Đếm số phòng chiếu."""
        return len(self.rooms)


class CinemaListResponse(PaginationResponse[CinemaResponse]):
    """Response danh sách rạp có phân trang.
    
    Kế thừa từ PaginationResponse[CinemaResponse].
    """
    pass


class RoomCreateRequest(BaseRequest):
    """Request tạo phòng chiếu mới.
    
    Khi tạo phòng, ghế sẽ được tự động generate dựa trên
    total_rows và seats_per_row.
    
    Attributes:
        name: Tên phòng (VD: "Phòng 1", "Hall A").
        room_type: Loại phòng (VD: "2D", "3D", "IMAX").
        total_rows: Số hàng ghế.
        seats_per_row: Số ghế mỗi hàng.
        patterns: Custom patterns cho loại ghế (optional).
            Nếu không truyền, dùng preset theo room_type.
        use_default_only: Nếu True và không có patterns,
            tất cả ghế sẽ là STANDARD.
    """
    name: str = Field(..., max_length=100)
    room_type: str = Field(..., max_length=50)
    total_rows: int = Field(..., gt=0)
    seats_per_row: int = Field(..., gt=0)

    patterns: list[SeatPattern] | None = Field(
        default=None,
        description="Custom patterns. Nếu không truyền sẽ dùng preset theo room_type."
    )

    use_default_only: bool = Field(
        default=False,
        description="Nếu True và không có patterns, tất cả ghế sẽ là STANDARD"
    )


class RoomUpdateRequest(BaseRequest):
    """Request cập nhật phòng chiếu.
    
    Lưu ý: Không thể update total_rows và seats_per_row
    vì sẽ ảnh hưởng đến cấu trúc ghế.
    
    Attributes:
        name: Tên phòng mới.
        room_type: Loại phòng mới.
        is_active: Trạng thái hoạt động.
    """
    name: str | None = Field(default=None, max_length=100)
    room_type: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class RoomResponse(BaseResponse):
    """Response chi tiết một phòng.
    
    Attributes:
        id: ID duy nhất của phòng.
        cinema_id: ID rạp chứa phòng.
        name: Tên phòng.
        room_type: Loại phòng.
        total_rows: Số hàng ghế.
        seats_per_row: Số ghế mỗi hàng.
        total_seats: Tổng số ghế.
        is_active: Phòng còn hoạt động không.
        created_at: Thời điểm tạo.
        updated_at: Thời điểm cập nhật.
    """
    id: UUID
    cinema_id: UUID
    name: str
    room_type: str
    total_rows: int
    seats_per_row: int
    total_seats: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoomListResponse(PaginationResponse[RoomResponse]):
    """Response danh sách phòng có phân trang.
    
    Kế thừa từ PaginationResponse[RoomResponse].
    """
    pass


class SeatCreateRequest(BaseRequest):
    """Request tạo ghế mới.
    
    Thường không cần dùng trực tiếp vì ghế được
    auto-generate khi tạo phòng.
    
    Attributes:
        row_label: Nhãn hàng (A-Z).
        seat_number: Số ghế trong hàng (> 0).
        seat_type: Loại ghế (mặc định STANDARD).
        price_multiplier: Hệ số giá (1.0 = chuẩn, 1.5 = VIP).
    """
    row_label: str = Field(..., pattern=r'^[A-Z]$')
    seat_number: int = Field(..., gt=0)
    seat_type: SeatType = Field(default=SeatType.STANDARD)
    price_multiplier: Decimal = Field(
        default=Decimal("1.00"),
        ge=1.00,
        le=3.00,
        description="Hệ số giá (1.0 = chuẩn, 1.5 = VIP)"
    )


class SeatUpdateRequest(BaseRequest):
    """Request cập nhật ghế.
    
    Thường dùng để thay đổi loại ghế hoặc vô hiệu hóa ghế.
    
    Attributes:
        seat_type: Loại ghế mới.
        price_multiplier: Hệ số giá mới.
        is_active: Ghế còn hoạt động không.
    """
    seat_type: SeatType | None = None
    price_multiplier: Decimal | None = Field(default=None, ge=1.0, le=3.0)
    is_active: bool | None = None


class SeatResponse(BaseResponse):
    """Response chi tiết một ghế.
    
    Attributes:
        id: ID duy nhất của ghế.
        room_id: ID phòng chứa ghế.
        row_label: Nhãn hàng.
        seat_number: Số ghế.
        seat_type: Loại ghế.
        price_multiplier: Hệ số giá.
        is_active: Ghế còn hoạt động không.
        created_at: Thời điểm tạo.
        seat_label: Nhãn đầy đủ (VD: "A1", "B12") (computed).
    """
    id: UUID
    room_id: UUID
    row_label: str
    seat_number: int
    seat_type: SeatType
    price_multiplier: Decimal
    is_active: bool
    created_at: datetime

    @computed_field
    @property
    def seat_label(self) -> str:
        """Tạo nhãn ghế đầy đủ, ví dụ: 'A1', 'B12'."""
        return f"{self.row_label}{self.seat_number}"


class SeatListResponse(PaginationResponse[SeatResponse]):
    """Response danh sách ghế có phân trang.
    
    Kế thừa từ PaginationResponse[SeatResponse].
    """
    pass


class BulkSeatCreateRequest(BaseRequest):
    """Request tạo nhiều ghế cùng lúc.
    
    Dùng khi cần tạo ghế thủ công thay vì auto-generate.
    
    Attributes:
        seats: Danh sách ghế cần tạo (1-1500).
    """
    seats: list[SeatCreateRequest] = Field(..., min_length=1, max_length=1500)
