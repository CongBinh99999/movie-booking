from pydantic import Field
from typing import Literal
from datetime import date, datetime
from uuid import UUID

from app.shared.schemas.base import (
    BaseResponse,
    BaseRequest
)
from app.shared.schemas.pagination import PaginationResponse
from typing import Literal


class MovieCreateRequest(BaseRequest):
    """Request tạo phim mới.

    Attributes:
        title: Tên phim tiếng Việt.
        original_title: Tên gốc của phim.
        description: Mô tả/giới thiệu phim.
        duration_minutes: Thời lượng phim (phút), từ 1-500.
        release_date: Ngày khởi chiếu.
        end_date: Ngày kết thúc chiếu.
        poster_url: Link ảnh poster.
        trailer_url: Link trailer.
        director: Tên đạo diễn.
        cast_members: Danh sách diễn viên.
        language: Ngôn ngữ gốc.
        subtitle: Ngôn ngữ phụ đề.
        age_rating: Độ tuổi xem phim (VD: "18+", "P").
    """
    title: str = Field(..., max_length=255)
    original_title: str = Field(..., max_length=255)
    description: str | None = None
    duration_minutes: int = Field(..., gt=0, le=500)
    release_date: date | None = None
    end_date: date | None = None
    poster_url: str | None = None
    trailer_url: str | None = None
    director: str | None = None
    cast_members: list[str] = Field(default_factory=list)
    language: str | None = None
    subtitle: str | None = None
    age_rating: str | None = None
    genre_ids: list[UUID] = Field(default_factory=list)


class MovieUpdateRequest(BaseRequest):
    """Request cập nhật thông tin phim.

    Tất cả các field đều optional. 
    Chỉ truyền field nào cần update.

    Attributes:
        title: Tên phim mới.
        original_title: Tên gốc mới.
        description: Mô tả mới.
        duration_minutes: Thời lượng mới (phút).
        release_date: Ngày khởi chiếu mới.
        end_date: Ngày kết thúc mới.
        poster_url: Link poster mới.
        trailer_url: Link trailer mới.
        director: Đạo diễn mới.
        cast_members: Danh sách diễn viên mới.
        language: Ngôn ngữ mới.
        subtitle: Phụ đề mới.
        age_rating: Độ tuổi mới.
    """
    title: str | None = None
    original_title: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    release_date: date | None = None
    end_date: date | None = None
    poster_url: str | None = None
    trailer_url: str | None = None
    director: str | None = None
    cast_members: list[str] | None = None
    language: str | None = None
    subtitle: str | None = None
    age_rating: str | None = None


class MovieResponse(BaseResponse):
    """Response chi tiết một phim.

    Trả về đầy đủ thông tin của một phim.

    Attributes:
        id: ID duy nhất của phim.
        title: Tên phim tiếng Việt.
        original_title: Tên gốc.
        description: Mô tả phim.
        duration_minutes: Thời lượng (phút).
        release_date: Ngày khởi chiếu.
        end_date: Ngày kết thúc.
        poster_url: Link poster.
        trailer_url: Link trailer.
        director: Đạo diễn.
        cast_members: Danh sách diễn viên.
        language: Ngôn ngữ gốc.
        subtitle: Phụ đề.
        age_rating: Độ tuổi.
        is_active: Phim còn hoạt động không.
        created_at: Thời điểm tạo.
        updated_at: Thời điểm cập nhật.
    """
    id: UUID
    title: str
    original_title: str
    description: str | None
    duration_minutes: int
    release_date: date | None
    end_date: date | None
    poster_url: str | None
    trailer_url: str | None
    director: str | None
    cast_members: list[str]
    language: str | None
    subtitle: str | None
    age_rating: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MovieListResponse(PaginationResponse[MovieResponse]):
    """Response danh sách phim có phân trang.

    Kế thừa từ PaginationResponse, cung cấp:
    - items: Danh sách MovieResponse của trang hiện tại.
    - total: Tổng số phim trong database.
    - page: Trang hiện tại.
    - size: Số phim mỗi trang.
    - pages: Tổng số trang (computed).
    - has_next: Có trang tiếp không (computed).
    - has_prev: Có trang trước không (computed).
    """
    pass


class GenreCreateRequest(BaseRequest):
    """Request tạo thể loại mới.

    Attributes:
        name: Tên thể loại (VD: "Hành động").
        slug: Slug URL-friendly (VD: "hanh-dong"). Tự động generate nếu không truyền.
    """
    name: str = Field(..., max_length=100)
    slug: str | None = Field(default=None, max_length=100)


class GenreUpdateRequest(BaseRequest):
    name: str | None = None
    slug: str | None = None


class GenreResponse(BaseResponse):
    """Response chi tiết một thể loại.

    Attributes:
        id: ID duy nhất.
        name: Tên thể loại.
        slug: Slug URL.
        created_at: Thời điểm tạo.
    """
    id: UUID
    name: str
    slug: str
    created_at: datetime


class GenreListResponse(PaginationResponse[GenreResponse]):
    """Response danh sách thể loại có phân trang.

    Kế thừa từ PaginationResponse[GenreResponse].
    """
    pass


class MovieQueryParams(BaseRequest):
    """Query parameters cho tìm kiếm phim.

    Dùng làm query params trong GET /movies endpoint.

    Attributes:
        title: Tìm theo tên phim (LIKE).
        original_title: Tìm theo tên gốc.
        release_date: Lọc theo ngày khởi chiếu.
        genre_ids: Lọc theo danh sách ID thể loại.
    """
    title: str | None = None
    original_title: str | None = None
    release_date: date | None = None
    genre_ids: list[UUID] | None = None
    status: Literal["now_showing", "coming_soon"] | None = None
    is_active: bool | None = None
    skip: int = 0
    limit: int = 20


class UpdateMovieGenresRequest(BaseRequest):
    """Request cập nhật thể loại cho phim.

    Attributes:
        genre_ids: Danh sách ID thể loại.
        action: "add" | "remove" | "replace"
    """
    genre_ids: list[UUID] = Field(default_factory=list)
    action: Literal["add", "remove", "replace"]
