"""Payments API schemas.

Các schema dùng cho API endpoints trong module payments.
Bao gồm Request và Response schemas.
"""
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from pydantic import Field, model_validator

from app.shared.schemas.base import BaseRequest, BaseResponse
from app.shared.schemas.nested import BookingBasic
from app.shared.schemas.pagination import PaginationResponse
from app.modules.payments.models import PaymentStatus, PaymentMethod


class PaymentCreateRequest(BaseRequest):
    """Request khởi tạo thanh toán.
    
    Tạo payment mới cho một booking, trả về URL
    để redirect user đến trang thanh toán.
    
    Attributes:
        booking_id: ID booking cần thanh toán.
        payment_method: Phương thức thanh toán (vnpay, momo, zalopay).
        return_url: URL redirect sau khi thanh toán xong.
    """
    booking_id: UUID = Field(..., description="ID booking cần thanh toán")
    payment_method: PaymentMethod = Field(..., description="Phương thức thanh toán")
    return_url: str | None = Field(
        None,
        max_length=500,
        description="URL redirect sau khi thanh toán"
    )


class PaymentCallbackRequest(BaseRequest):
    """Request callback từ cổng thanh toán.
    
    Nhận callback từ VNPay/Momo/ZaloPay sau khi user thanh toán.
    Raw data sẽ được parse theo từng loại payment_method.
    
    Attributes:
        raw_data: Dữ liệu callback raw từ cổng thanh toán.
    """
    raw_data: dict = Field(
        default_factory=dict,
        description="Raw callback data từ cổng thanh toán"
    )


class PaymentResponse(BaseResponse):
    """Response chi tiết một payment.
    
    Trả về đầy đủ thông tin của một thanh toán.
    
    Attributes:
        id: ID duy nhất của payment.
        booking_id: ID booking liên quan.
        transaction_id: Mã giao dịch từ cổng thanh toán.
        payment_method: Phương thức thanh toán.
        amount: Số tiền (VND).
        status: Trạng thái thanh toán.
        payment_url: URL trang thanh toán.
        paid_at: Thời điểm thanh toán thành công.
        failed_at: Thời điểm thất bại.
        failure_reason: Lý do thất bại.
        created_at: Thời điểm tạo.
        updated_at: Thời điểm cập nhật.
        booking: Thông tin booking (optional).
    """
    id: UUID
    booking_id: UUID
    transaction_id: str | None
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus
    payment_url: str | None
    paid_at: datetime | None
    failed_at: datetime | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime
    booking: BookingBasic | None = None


class PaymentListResponse(PaginationResponse[PaymentResponse]):
    """Response danh sách payment có phân trang.
    
    Kế thừa từ PaginationResponse[PaymentResponse].
    Cung cấp items, total, page, size, pages, has_next, has_prev.
    """
    pass


class RefundRequest(BaseRequest):
    """Request hoàn tiền.
    
    Yêu cầu hoàn tiền cho một payment đã thanh toán thành công.
    
    Attributes:
        payment_id: ID payment cần hoàn tiền.
        amount: Số tiền hoàn (None = hoàn toàn bộ).
        reason: Lý do hoàn tiền.
    """
    payment_id: UUID = Field(..., description="ID payment cần hoàn tiền")
    amount: Decimal | None = Field(
        None,
        gt=0,
        description="Số tiền hoàn (None = hoàn toàn bộ)"
    )
    reason: str = Field(
        ...,
        max_length=500,
        description="Lý do hoàn tiền"
    )


class PaymentQueryParams(BaseRequest):
    """Query parameters cho tìm kiếm payment.
    
    Dùng làm query params trong GET /payments endpoint.
    
    Attributes:
        booking_id: Lọc theo booking.
        status: Lọc theo trạng thái.
        payment_method: Lọc theo phương thức.
        transaction_id: Tìm theo mã giao dịch.
        date_from: Lọc từ ngày.
        date_to: Lọc đến ngày.
    """
    booking_id: UUID | None = Field(None, description="Lọc theo booking")
    status: PaymentStatus | None = Field(None, description="Lọc theo trạng thái")
    payment_method: PaymentMethod | None = Field(
        None,
        description="Lọc theo phương thức"
    )
    transaction_id: str | None = Field(
        None,
        description="Tìm theo mã giao dịch"
    )
    date_from: datetime | None = Field(None, description="Từ ngày")
    date_to: datetime | None = Field(None, description="Đến ngày")

    @model_validator(mode='after')
    def validate_date_range(self) -> 'PaymentQueryParams':
        """Kiểm tra date_from phải trước date_to."""
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("date_from phải trước hoặc bằng date_to")
        return self
