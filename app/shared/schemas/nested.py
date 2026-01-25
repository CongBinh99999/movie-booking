"""Shared nested schemas.

Các schema cơ bản (Basic) dùng để nhúng vào các schema khác,
tránh circular dependency giữa các modules.

Các schema này chỉ chứa các field quan trọng nhất,
được dùng khi hiển thị thông tin liên kết.
"""
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.modules.cinemas.models import SeatType
from app.modules.bookings.models import BookingStatus
from app.shared.schemas.base import BaseSchema


class MovieBasic(BaseSchema):
    """Thông tin phim cơ bản.
    
    Dùng khi nhúng thông tin phim vào các schema khác,
    như ShowtimeResponse, BookingResponse.
    
    Attributes:
        id: ID duy nhất của phim.
        title: Tên phim tiếng Việt.
        poster_url: Link ảnh poster.
        duration_minutes: Thời lượng phim (phút).
    """
    id: UUID
    title: str
    poster_url: str | None = None
    duration_minutes: int


class CinemaBasic(BaseSchema):
    """Thông tin rạp cơ bản.
    
    Dùng khi nhúng thông tin rạp vào các schema khác,
    như ShowtimeResponse, RoomResponse.
    
    Attributes:
        id: ID duy nhất của rạp.
        name: Tên rạp.
        city: Thành phố.
    """
    id: UUID
    name: str
    city: str


class RoomBasic(BaseSchema):
    """Thông tin phòng chiếu cơ bản.
    
    Dùng khi nhúng thông tin phòng vào các schema khác,
    như ShowtimeResponse, SeatResponse.
    
    Attributes:
        id: ID duy nhất của phòng.
        name: Tên phòng (VD: "Phòng 1", "Hall A").
        room_type: Loại phòng (VD: "2D", "3D", "IMAX").
    """
    id: UUID
    name: str
    room_type: str


class SeatBasic(BaseSchema):
    """Thông tin ghế cơ bản.
    
    Dùng khi nhúng thông tin ghế vào các schema khác,
    như BookingResponse.
    
    Attributes:
        id: ID duy nhất của ghế.
        row_label: Nhãn hàng (VD: "A", "B", "C").
        seat_number: Số ghế trong hàng (VD: 1, 2, 3).
        seat_type: Loại ghế (standard, vip, couple).
    """
    id: UUID
    row_label: str
    seat_number: int
    seat_type: SeatType


class ShowtimeBasic(BaseSchema):
    """Thông tin suất chiếu cơ bản.
    
    Dùng khi nhúng thông tin suất chiếu vào các schema khác,
    như BookingResponse.
    
    Attributes:
        id: ID duy nhất của suất chiếu.
        start_time: Thời gian bắt đầu.
        end_time: Thời gian kết thúc.
    """
    id: UUID
    start_time: datetime
    end_time: datetime


class UserBasic(BaseSchema):
    """Thông tin user cơ bản.
    
    Dùng khi nhúng thông tin user vào các schema khác,
    như BookingResponse (admin view).
    
    Attributes:
        id: ID duy nhất của user.
        username: Tên đăng nhập.
        email: Email.
    """
    id: UUID
    username: str
    email: str


class BookingBasic(BaseSchema):
    """Thông tin booking cơ bản.
    
    Dùng khi nhúng thông tin booking vào các schema khác,
    như PaymentResponse.
    
    Attributes:
        id: ID duy nhất của booking.
        booking_code: Mã đặt vé (VD: "BK20240124001").
        status: Trạng thái booking.
        total_amount: Tổng tiền (VND).
    """
    id: UUID
    booking_code: str
    status: BookingStatus
    total_amount: Decimal
