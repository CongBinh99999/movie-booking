"""Movies domain schemas.

Các schema dùng cho business logic và transfer data
giữa các layer trong module movies.
"""
from app.shared.schemas.base import BaseSchema
from app.shared.schemas.nested import (
    MovieBasic,
    ShowtimeBasic,
    CinemaBasic,
    RoomBasic
)

from uuid import UUID
from decimal import Decimal
from datetime import date, datetime
from pydantic import Field, computed_field


class GenreDTO(BaseSchema):
    """Schema đầy đủ cho Genre (thể loại phim).
    
    Attributes:
        id: ID duy nhất của thể loại.
        name: Tên thể loại (VD: "Hành động", "Kinh dị").
        slug: Slug URL-friendly (VD: "hanh-dong", "kinh-di").
        created_at: Thời điểm tạo record.
    """
    id: UUID
    name: str
    slug: str
    created_at: datetime


class MovieDTO(MovieBasic):
    """Schema đầy đủ cho Movie.
    
    Kế thừa từ MovieBasic (id, title, poster_url, duration_minutes)
    và bổ sung các thông tin chi tiết.
    
    Attributes:
        original_title: Tên gốc của phim (tiếng nước ngoài).
        description: Mô tả/giới thiệu phim.
        release_date: Ngày khởi chiếu.
        end_date: Ngày kết thúc chiếu.
        trailer_url: Link trailer phim.
        director: Tên đạo diễn.
        cast_members: Danh sách diễn viên.
        language: Ngôn ngữ gốc.
        subtitle: Ngôn ngữ phụ đề.
        age_rating: Độ tuổi xem phim (VD: "18+", "P").
        is_active: Phim còn hoạt động không.
        created_at: Thời điểm tạo record.
        updated_at: Thời điểm cập nhật gần nhất.
    """
    original_title: str
    description: str | None
    release_date: date | None
    end_date: date | None
    trailer_url: str | None
    director: str | None
    cast_members: list[str]
    language: str | None
    subtitle: str | None
    age_rating: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MovieWithGenres(MovieBasic):
    """Movie kèm danh sách thể loại.
    
    Dùng khi cần hiển thị phim cùng các thể loại của nó.
    
    Attributes:
        genres: Danh sách các thể loại của phim.
    """
    genres: list[GenreDTO] = Field(default_factory=list)


class MovieWithShowtimes(MovieBasic):
    """Movie kèm danh sách suất chiếu.
    
    Dùng khi cần hiển thị phim cùng các suất chiếu.
    
    Attributes:
        showtimes: Danh sách suất chiếu của phim.
    """
    showtimes: list[ShowtimeBasic] = Field(default_factory=list)


class NowShowingMovie(MovieBasic):
    """Phim đang chiếu.
    
    Schema cho danh sách phim đang chiếu tại rạp,
    tức là có suất chiếu trong khoảng thời gian hiện tại.
    
    Attributes:
        release_date: Ngày khởi chiếu.
        age_rating: Độ tuổi xem phim.
        genres: Danh sách tên thể loại (string, không phải GenreDTO).
    """
    release_date: date | None = None
    age_rating: str | None = None
    genres: list[str] = Field(default_factory=list)


class ComingSoonMovie(MovieBasic):
    """Phim sắp chiếu.
    
    Schema cho danh sách phim sắp chiếu,
    tức là có release_date > ngày hiện tại.
    
    Attributes:
        release_date: Ngày khởi chiếu (bắt buộc).
        trailer_url: Link trailer để quảng bá.
        description: Mô tả ngắn về phim.
        age_rating: Độ tuổi xem phim.
        genres: Danh sách tên thể loại.
    """
    release_date: date
    trailer_url: str | None = None
    description: str | None = None
    age_rating: str | None = None
    genres: list[str] = Field(default_factory=list)


class MovieSearchCriteria(BaseSchema):
    """Tiêu chí tìm kiếm phim.
    
    Dùng trong service layer để filter phim theo các điều kiện.
    
    Attributes:
        title: Tìm theo tên phim (LIKE search).
        original_title: Tìm theo tên gốc.
        release_date: Lọc theo ngày khởi chiếu cụ thể.
    """
    title: str | None = None
    original_title: str | None = None
    release_date: date | None = None
