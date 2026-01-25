"""Showtimes domain schemas.

Các schema dùng cho business logic và transfer data
giữa các layer trong module showtimes.
"""
from app.shared.schemas.base import BaseSchema
from app.shared.schemas.nested import (
    ShowtimeBasic,
    MovieBasic,
    CinemaBasic,
    RoomBasic,
    SeatBasic
)

from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from pydantic import Field, model_validator


class ShowtimeDTO(ShowtimeBasic):
    """Schema đầy đủ cho Showtime (suất chiếu).
    
    Kế thừa từ ShowtimeBasic (id, start_time, end_time)
    và bổ sung các thông tin chi tiết.
    
    Attributes:
        movie_id: ID phim được chiếu.
        room_id: ID phòng chiếu.
        base_price: Giá vé cơ bản (chưa nhân hệ số ghế).
        is_active: Suất chiếu còn hoạt động không.
        created_at: Thời điểm tạo record.
        updated_at: Thời điểm cập nhật gần nhất.
    """
    movie_id: UUID
    room_id: UUID
    base_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ShowtimeWithDetails(ShowtimeBasic):
    """Suất chiếu kèm thông tin chi tiết.
    
    Dùng khi cần hiển thị suất chiếu cùng thông tin
    phim, phòng chiếu và rạp.
    
    Attributes:
        base_price: Giá vé cơ bản.
        is_active: Suất chiếu còn hoạt động không.
        movie: Thông tin cơ bản về phim.
        room: Thông tin cơ bản về phòng chiếu.
        cinema: Thông tin cơ bản về rạp.
    """
    base_price: Decimal
    is_active: bool
    movie: MovieBasic
    room: RoomBasic
    cinema: CinemaBasic


class SeatAvailability(SeatBasic):
    """Thông tin ghế kèm trạng thái có sẵn.
    
    Dùng khi hiển thị sơ đồ ghế cho một suất chiếu,
    cho biết ghế nào còn trống, ghế nào đã đặt.
    
    Attributes:
        price_multiplier: Hệ số giá (VD: 1.5 cho VIP).
        is_available: Ghế còn trống không.
        final_price: Giá cuối cùng (base_price × multiplier).
    """
    price_multiplier: Decimal
    is_available: bool = True
    final_price: Decimal | None = None


class ShowtimeWithSeats(ShowtimeBasic):
    """Suất chiếu kèm danh sách ghế và trạng thái.
    
    Dùng cho màn hình chọn ghế, hiển thị sơ đồ ghế
    với trạng thái có sẵn của từng ghế.
    
    Attributes:
        base_price: Giá vé cơ bản.
        movie: Thông tin phim.
        room: Thông tin phòng chiếu.
        cinema: Thông tin rạp.
        seats: Danh sách ghế với trạng thái available.
    """
    base_price: Decimal
    movie: MovieBasic
    room: RoomBasic
    cinema: CinemaBasic
    seats: list[SeatAvailability] = Field(default_factory=list)


class ShowtimeSearchCriteria(BaseSchema):
    """Tiêu chí tìm kiếm suất chiếu.
    
    Dùng trong service layer để filter suất chiếu.
    
    Attributes:
        movie_id: Lọc theo phim.
        room_id: Lọc theo phòng chiếu.
        cinema_id: Lọc theo rạp.
        date_from: Lọc từ thời điểm.
        date_to: Lọc đến thời điểm.
        is_active: Lọc theo trạng thái hoạt động.
    """
    movie_id: UUID | None = Field(None, description="Lọc theo phim")
    room_id: UUID | None = Field(None, description="Lọc theo phòng")
    cinema_id: UUID | None = Field(None, description="Lọc theo rạp")
    date_from: datetime | None = Field(None, description="Từ thời điểm")
    date_to: datetime | None = Field(None, description="Đến thời điểm")
    is_active: bool | None = Field(None, description="Lọc theo trạng thái")

    @model_validator(mode='after')
    def validate_date_range(self) -> 'ShowtimeSearchCriteria':
        """Kiểm tra date_from phải trước date_to."""
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("date_from phải trước hoặc bằng date_to")
        return self


class DailyShowtimeSchedule(BaseSchema):
    """Lịch chiếu theo ngày.
    
    Dùng để hiển thị tất cả suất chiếu của một phim
    trong một ngày cụ thể.
    
    Attributes:
        date: Ngày chiếu.
        movie: Thông tin phim.
        showtimes: Danh sách suất chiếu trong ngày.
    """
    date: date
    movie: MovieBasic
    showtimes: list[ShowtimeWithDetails] = Field(default_factory=list)


class ShowtimeConflictCheck(BaseSchema):
    """Schema kiểm tra xung đột lịch chiếu.
    
    Dùng để kiểm tra xem một suất chiếu mới có
    xung đột với các suất chiếu hiện có không.
    
    Attributes:
        room_id: ID phòng chiếu cần kiểm tra.
        start_time: Thời gian bắt đầu dự kiến.
        end_time: Thời gian kết thúc dự kiến.
        exclude_showtime_id: ID suất chiếu cần loại trừ
            (dùng khi update suất chiếu hiện có).
    """
    room_id: UUID
    start_time: datetime
    end_time: datetime
    exclude_showtime_id: UUID | None = Field(
        None,
        description="ID suất chiếu cần loại trừ (khi update)"
    )

    @model_validator(mode='after')
    def validate_time_range(self) -> 'ShowtimeConflictCheck':
        """Kiểm tra start_time phải trước end_time."""
        if self.start_time >= self.end_time:
            raise ValueError("start_time phải trước end_time")
        return self
