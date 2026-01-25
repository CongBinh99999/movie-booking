"""Showtimes API schemas.

Các schema dùng cho API endpoints trong module showtimes.
Bao gồm Request và Response schemas.
"""
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date

from pydantic import Field, model_validator

from app.shared.schemas.base import BaseRequest, BaseResponse
from app.shared.schemas.nested import (
    MovieBasic,
    RoomBasic,
    CinemaBasic
)
from app.shared.schemas.pagination import PaginationResponse


class ShowtimeCreateRequest(BaseRequest):
    """Request tạo suất chiếu mới.
    
    Thời gian kết thúc (end_time) sẽ được tính tự động
    dựa trên start_time + duration_minutes của phim.
    
    Attributes:
        movie_id: ID phim được chiếu.
        room_id: ID phòng chiếu.
        start_time: Thời gian bắt đầu chiếu.
        base_price: Giá vé cơ bản (VND).
    """
    movie_id: UUID = Field(..., description="ID phim")
    room_id: UUID = Field(..., description="ID phòng chiếu")
    start_time: datetime = Field(..., description="Thời gian bắt đầu")
    base_price: Decimal = Field(
        ...,
        gt=0,
        le=10000000,
        description="Giá vé cơ bản"
    )


class ShowtimeUpdateRequest(BaseRequest):
    """Request cập nhật suất chiếu.
    
    Tất cả field đều optional.
    Chỉ truyền field nào cần update.
    
    Attributes:
        start_time: Thời gian bắt đầu mới.
        base_price: Giá vé mới.
        is_active: Trạng thái hoạt động mới.
    """
    start_time: datetime | None = Field(None, description="Thời gian bắt đầu mới")
    base_price: Decimal | None = Field(
        None,
        gt=0,
        le=10000000,
        description="Giá vé cơ bản mới"
    )
    is_active: bool | None = Field(None, description="Trạng thái hoạt động")


class ShowtimeResponse(BaseResponse):
    """Response chi tiết một suất chiếu.
    
    Trả về đầy đủ thông tin suất chiếu kèm phim, phòng, rạp.
    
    Attributes:
        id: ID duy nhất của suất chiếu.
        start_time: Thời gian bắt đầu.
        end_time: Thời gian kết thúc.
        base_price: Giá vé cơ bản.
        is_active: Suất chiếu còn hoạt động không.
        created_at: Thời điểm tạo.
        updated_at: Thời điểm cập nhật.
        movie: Thông tin phim.
        room: Thông tin phòng chiếu.
        cinema: Thông tin rạp.
    """
    id: UUID
    start_time: datetime
    end_time: datetime
    base_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    movie: MovieBasic
    room: RoomBasic
    cinema: CinemaBasic


class ShowtimeListResponse(PaginationResponse[ShowtimeResponse]):
    """Response danh sách suất chiếu có phân trang.
    
    Kế thừa từ PaginationResponse[ShowtimeResponse].
    Cung cấp items, total, page, size, pages, has_next, has_prev.
    """
    pass


class ShowtimeQueryParams(BaseRequest):
    """Query parameters cho tìm kiếm suất chiếu.
    
    Dùng làm query params trong GET /showtimes endpoint.
    
    Attributes:
        movie_id: Lọc theo phim.
        room_id: Lọc theo phòng.
        cinema_id: Lọc theo rạp.
        filter_date: Lọc theo ngày cụ thể.
        date_from: Lọc từ thời điểm.
        date_to: Lọc đến thời điểm.
        is_active: Chỉ lấy suất chiếu active (mặc định True).
    """
    movie_id: UUID | None = Field(None, description="Lọc theo phim")
    room_id: UUID | None = Field(None, description="Lọc theo phòng")
    cinema_id: UUID | None = Field(None, description="Lọc theo rạp")
    filter_date: date | None = Field(None, description="Lọc theo ngày")
    date_from: datetime | None = Field(None, description="Từ thời điểm")
    date_to: datetime | None = Field(None, description="Đến thời điểm")
    is_active: bool | None = Field(True, description="Chỉ lấy suất chiếu active")

    @model_validator(mode='after')
    def validate_date_range(self) -> 'ShowtimeQueryParams':
        """Kiểm tra date_from phải trước date_to."""
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("date_from phải trước hoặc bằng date_to")
        return self


class BulkShowtimeItem(BaseRequest):
    """Một item trong bulk create request.
    
    Attributes:
        room_id: ID phòng chiếu.
        start_time: Thời gian bắt đầu.
        base_price: Giá vé cơ bản.
    """
    room_id: UUID
    start_time: datetime
    base_price: Decimal = Field(..., gt=0)


class BulkShowtimeCreateRequest(BaseRequest):
    """Request tạo nhiều suất chiếu cùng lúc cho 1 phim.
    
    Dùng để tạo lịch chiếu hàng loạt, ví dụ:
    tạo suất chiếu cho 1 phim ở nhiều phòng/giờ khác nhau.
    
    Attributes:
        movie_id: ID phim (chung cho tất cả suất chiếu).
        showtimes: Danh sách suất chiếu cần tạo (tối đa 50).
    """
    movie_id: UUID = Field(..., description="ID phim")
    showtimes: list[BulkShowtimeItem] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Danh sách suất chiếu (tối đa 50)"
    )
