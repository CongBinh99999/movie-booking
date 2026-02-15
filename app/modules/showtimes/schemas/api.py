"""Showtimes API schemas.

Các schema dùng cho API endpoints trong module showtimes.
Bao gồm Request và Response schemas.
"""
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timezone, timedelta

from pydantic import Field, field_validator, model_validator

from app.shared.schemas.base import BaseRequest, BaseResponse
from app.shared.schemas.nested import (
    MovieBasic,
    RoomBasic,
    CinemaBasic
)
from app.shared.schemas.pagination import PaginationResponse

# -- Constants --
MIN_SHOWTIME_DURATION_MINUTES = 30
MAX_SHOWTIME_DURATION_HOURS = 6
MAX_BASE_PRICE = 10_000_000
MAX_BASE_PRICE_DECIMAL_PLACES = 2


class ShowtimeCreateRequest(BaseRequest):
    """Request tạo suất chiếu mới.

    Validators:
        - start_time phải ở tương lai.
        - end_time phải sau start_time.
        - Thời lượng tối thiểu 30 phút, tối đa 6 giờ.
        - base_price > 0, tối đa 10,000,000, tối đa 2 chữ số thập phân.
    """
    movie_id: UUID = Field(..., description="ID phim")
    room_id: UUID = Field(..., description="ID phòng chiếu")
    start_time: datetime = Field(..., description="Thời gian bắt đầu")
    end_time: datetime = Field(..., description="Thời gian kết thúc")
    base_price: Decimal = Field(
        ...,
        gt=0,
        le=MAX_BASE_PRICE,
        description="Giá vé cơ bản (VND)"
    )

    @field_validator("start_time")
    @classmethod
    def validate_start_time_in_future(cls, value: datetime) -> datetime:
        """start_time phải ở tương lai."""
        now = datetime.now(timezone.utc)
        # So sánh aware datetime
        compare_value = value if value.tzinfo else value.replace(
            tzinfo=timezone.utc)
        if compare_value <= now:
            raise ValueError("start_time phải ở tương lai")
        return value

    @field_validator("base_price")
    @classmethod
    def validate_base_price_scale(cls, value: Decimal) -> Decimal:
        """base_price chỉ được có tối đa 2 chữ số thập phân."""
        exponent = value.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -MAX_BASE_PRICE_DECIMAL_PLACES:
            raise ValueError(
                f"base_price chỉ được có tối đa {MAX_BASE_PRICE_DECIMAL_PLACES} chữ số thập phân"
            )
        return value

    @model_validator(mode="after")
    def validate_time_range(self) -> "ShowtimeCreateRequest":
        """Kiểm tra logic thời gian: start < end, duration hợp lệ."""
        if self.start_time >= self.end_time:
            raise ValueError("start_time phải trước end_time")

        duration = self.end_time - self.start_time
        min_duration = timedelta(minutes=MIN_SHOWTIME_DURATION_MINUTES)
        max_duration = timedelta(hours=MAX_SHOWTIME_DURATION_HOURS)

        if duration < min_duration:
            raise ValueError(
                f"Thời lượng suất chiếu phải tối thiểu {MIN_SHOWTIME_DURATION_MINUTES} phút"
            )
        if duration > max_duration:
            raise ValueError(
                f"Thời lượng suất chiếu không được vượt quá {MAX_SHOWTIME_DURATION_HOURS} giờ"
            )
        return self


class ShowtimeUpdateRequest(BaseRequest):
    """Request cập nhật suất chiếu.

    Tất cả field đều optional.

    Validators:
        - Nếu có cả start_time và end_time: start < end, duration 30 phút - 6 giờ.
        - base_price tối đa 2 chữ số thập phân.
    """
    start_time: datetime | None = Field(
        None,
        description="Thời gian bắt đầu mới"
    )
    end_time: datetime | None = Field(
        None,
        description="Thời gian kết thúc mới"
    )
    base_price: Decimal | None = Field(
        None,
        gt=0,
        le=MAX_BASE_PRICE,
        description="Giá vé cơ bản mới (VND)"
    )
    is_active: bool | None = Field(
        None,
        description="Trạng thái hoạt động"
    )

    @field_validator("base_price")
    @classmethod
    def validate_base_price_scale(cls, value: Decimal | None) -> Decimal | None:
        """base_price chỉ được có tối đa 2 chữ số thập phân."""
        if value is not None:
            exponent = value.as_tuple().exponent
            if isinstance(exponent, int) and exponent < -MAX_BASE_PRICE_DECIMAL_PLACES:
                raise ValueError(
                    f"base_price chỉ được có tối đa {MAX_BASE_PRICE_DECIMAL_PLACES} chữ số thập phân"
                )
        return value

    @model_validator(mode="after")
    def validate_time_range(self) -> "ShowtimeUpdateRequest":
        """Kiểm tra logic thời gian khi cả 2 field được truyền."""
        if self.start_time is None or self.end_time is None:
            return self

        if self.start_time >= self.end_time:
            raise ValueError("start_time phải trước end_time")

        duration = self.end_time - self.start_time
        min_duration = timedelta(minutes=MIN_SHOWTIME_DURATION_MINUTES)
        max_duration = timedelta(hours=MAX_SHOWTIME_DURATION_HOURS)

        if duration < min_duration:
            raise ValueError(
                f"Thời lượng suất chiếu phải tối thiểu {MIN_SHOWTIME_DURATION_MINUTES} phút"
            )
        if duration > max_duration:
            raise ValueError(
                f"Thời lượng suất chiếu không được vượt quá {MAX_SHOWTIME_DURATION_HOURS} giờ"
            )
        return self


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
    movie_id: UUID
    room_id: UUID
    start_time: datetime
    end_time: datetime
    base_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    movie: MovieBasic | None = None
    room: RoomBasic | None = None
    cinema: CinemaBasic | None = None


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
    is_active: bool | None = Field(
        True, description="Chỉ lấy suất chiếu active")

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
        end_time: Thời gian kết thúc.
        base_price: Giá vé cơ bản.
    """
    room_id: UUID
    start_time: datetime
    end_time: datetime
    base_price: Decimal = Field(..., gt=0, le=MAX_BASE_PRICE)

    @field_validator("start_time")
    @classmethod
    def validate_start_time_in_future(cls, value: datetime) -> datetime:
        """start_time phải ở tương lai."""
        now = datetime.now(timezone.utc)
        compare_value = value if value.tzinfo else value.replace(
            tzinfo=timezone.utc)
        if compare_value <= now:
            raise ValueError("start_time phải ở tương lai")
        return value

    @field_validator("base_price")
    @classmethod
    def validate_base_price_scale(cls, value: Decimal) -> Decimal:
        """base_price chỉ được có tối đa 2 chữ số thập phân."""
        exponent = value.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -MAX_BASE_PRICE_DECIMAL_PLACES:
            raise ValueError(
                f"base_price chỉ được có tối đa {MAX_BASE_PRICE_DECIMAL_PLACES} chữ số thập phân"
            )
        return value

    @model_validator(mode="after")
    def validate_time_range(self) -> "BulkShowtimeItem":
        """Kiểm tra start_time phải trước end_time và duration hợp lệ."""
        if self.start_time >= self.end_time:
            raise ValueError("start_time phải trước end_time")

        duration = self.end_time - self.start_time
        if duration < timedelta(minutes=MIN_SHOWTIME_DURATION_MINUTES):
            raise ValueError(
                f"Thời lượng suất chiếu phải tối thiểu {MIN_SHOWTIME_DURATION_MINUTES} phút"
            )
        if duration > timedelta(hours=MAX_SHOWTIME_DURATION_HOURS):
            raise ValueError(
                f"Thời lượng suất chiếu không được vượt quá {MAX_SHOWTIME_DURATION_HOURS} giờ"
            )
        return self


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
