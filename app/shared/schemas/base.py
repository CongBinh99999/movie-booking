from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    """Schema cơ sở cho tất cả schemas trong ứng dụng.
    
    Cung cấp cấu hình chung cho tất cả Pydantic models.
    
    Config:
        from_attributes: Cho phép tạo schema từ ORM model
            (VD: MovieResponse.model_validate(movie_model)).
        populate_by_name: Cho phép dùng cả field name và alias.
        str_strip_whitespace: Tự động strip whitespace ở string.
    
    Example:
        class MovieDTO(BaseSchema):
            id: UUID
            title: str
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True
    )


class BaseRequest(BaseSchema):
    """Schema cơ sở cho API request.
    
    Kế thừa từ BaseSchema và thêm validation nghiêm ngặt hơn
    cho dữ liệu đầu vào từ client.
    
    Config:
        extra="forbid": Không cho phép truyền field không được
            định nghĩa trong schema. Điều này giúp bắt lỗi
            khi client gửi field sai tên.
    
    Example:
        class MovieCreateRequest(BaseRequest):
            title: str
            duration_minutes: int
        
        # Sẽ lỗi nếu client gửi:
        # {"title": "ABC", "duration": 120}  # 'duration' không hợp lệ
    """
    model_config = ConfigDict(
        extra="forbid"
    )


class BaseResponse(BaseSchema):
    """Schema cơ sở cho API response.
    
    Kế thừa từ BaseSchema, hiện tại chưa có config đặc biệt.
    Có thể mở rộng sau này nếu cần thêm logic chung
    cho response (VD: thêm metadata, status code).
    
    Example:
        class MovieResponse(BaseResponse):
            id: UUID
            title: str
            created_at: datetime
    """
    pass


class TimeStampMixin(BaseModel):
    """Mixin cung cấp các trường timestamp.
    
    Dùng để thêm created_at và updated_at vào schema
    mà không cần định nghĩa lại.
    
    Attributes:
        created_at: Thời điểm tạo record.
        updated_at: Thời điểm cập nhật gần nhất.
    
    Example:
        class MovieDTO(BaseSchema, TimeStampMixin):
            id: UUID
            title: str
            # Tự động có created_at và updated_at
    """
    created_at: datetime
    updated_at: datetime


class IdentifiableMixin(BaseModel):
    """Mixin cung cấp trường id.
    
    Dùng để thêm UUID id vào schema mà không cần định nghĩa lại.
    
    Attributes:
        id: UUID duy nhất của entity.
    
    Example:
        class MovieDTO(BaseSchema, IdentifiableMixin, TimeStampMixin):
            title: str
            # Tự động có id, created_at, updated_at
    """
    id: UUID
