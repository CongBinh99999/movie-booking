"""Pagination schemas cho phân trang dữ liệu.

Module này cung cấp các class để xử lý phân trang,
bao gồm tham số đầu vào và response format chuẩn.

Classes:
    PaginationParams: Tham số phân trang từ client.
    PaginationResponse: Response format chuẩn có phân trang.
"""
from math import ceil
from pydantic import BaseModel, Field, computed_field
from typing import TypeVar, Generic

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Tham số phân trang từ client.

    Dùng làm dependency trong FastAPI router để parse
    query params ?page=1&size=20.

    Attributes:
        page: Số trang hiện tại (bắt đầu từ 1).
        size: Số records mỗi trang (1-100, mặc định 20).

    Properties:
        offset: Số records cần bỏ qua = (page - 1) × size.
            Dùng cho SQL OFFSET clause.

    Example:
        # Page 1, size 20 → offset = 0, lấy records 1-20
        # Page 2, size 20 → offset = 20, lấy records 21-40
        # Page 3, size 20 → offset = 40, lấy records 41-60

    Usage:
        @router.get("/movies")
        def list_movies(pagination: PaginationParams = Depends()):
            movies = repo.get_all(
                offset=pagination.offset,
                limit=pagination.size
            )
    """
    page: int = Field(default=1, ge=1, description="Số trang (bắt đầu từ 1)")
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Số records mỗi trang (1-100)"
    )

    @property
    def offset(self) -> int:
        """Tính offset cho SQL query.

        Công thức: offset = (page - 1) × size

        Returns:
            Số records cần bỏ qua từ đầu.

        Example:
            page=1, size=20 → offset=0
            page=2, size=20 → offset=20
            page=3, size=20 → offset=40
        """
        return (self.page - 1) * self.size


class PaginationResponse(BaseModel, Generic[T]):
    """Response format chuẩn có phân trang.

    Generic class hỗ trợ type-safe cho items.
    Kế thừa class này để tạo ListResponse cho từng entity.

    Attributes:
        items: Danh sách records của trang hiện tại.
        total: Tổng số records trong database (không phải len(items)).
        page: Trang hiện tại.
        size: Số records mỗi trang.

    Computed Properties:
        pages: Tổng số trang = ceil(total / size).
        has_next: Có trang tiếp theo không (page < pages).
        has_prev: Có trang trước không (page > 1).

    Example:
        class MovieListResponse(PaginationResponse[MovieResponse]):
            pass

        # Response sẽ có dạng:
        # {
        #     "items": [...],  # list[MovieResponse]
        #     "total": 150,
        #     "page": 1,
        #     "size": 20,
        #     "pages": 8,
        #     "has_next": true,
        #     "has_prev": false
        # }

    Usage:
        return MovieListResponse(
            items=movies,      # Danh sách phim trang hiện tại
            total=total_count, # Tổng số phim trong DB
            page=page,         # Trang hiện tại
            size=size          # Số phim mỗi trang
        )
    """
    items: list[T] = Field(description="Danh sách records của trang hiện tại")
    total: int = Field(description="Tổng số records trong database")
    page: int = Field(description="Trang hiện tại")
    size: int = Field(description="Số records mỗi trang")

    @computed_field
    @property
    def pages(self) -> int:
        """Tính tổng số trang.

        Công thức: pages = ceil(total / size)

        Returns:
            Tổng số trang. Trả về 0 nếu size = 0.

        Example:
            total=95, size=20 → pages=5 (20+20+20+20+15)
            total=100, size=20 → pages=5
            total=0, size=20 → pages=0
        """
        return ceil(self.total / self.size) if self.size > 0 else 0

    @computed_field
    @property
    def has_next(self) -> bool:
        """Kiểm tra có trang tiếp theo không.

        Returns:
            True nếu page < pages, nghĩa là còn trang sau.

        Example:
            page=1, pages=5 → has_next=True
            page=5, pages=5 → has_next=False
        """
        return self.page < self.pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        """Kiểm tra có trang trước không.

        Returns:
            True nếu page > 1, nghĩa là có trang trước.

        Example:
            page=1 → has_prev=False
            page=2 → has_prev=True
        """
        return self.page > 1
