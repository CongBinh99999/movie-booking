"""Payments domain schemas.

Các schema dùng cho business logic và transfer data
giữa các layer trong module payments.
"""
from app.shared.schemas.base import BaseSchema
from app.shared.schemas.nested import BookingBasic
from app.modules.payments.models import PaymentStatus, PaymentMethod

from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Any
from pydantic import Field


class PaymentDTO(BaseSchema):
    """Schema đầy đủ cho Payment (thanh toán).
    
    Attributes:
        id: ID duy nhất của payment.
        booking_id: ID booking liên quan.
        transaction_id: Mã giao dịch từ cổng thanh toán.
        payment_method: Phương thức thanh toán (VNPay, Momo, ZaloPay).
        amount: Số tiền thanh toán (VND).
        status: Trạng thái thanh toán.
        payment_url: URL redirect đến trang thanh toán.
        callback_data: Dữ liệu callback từ cổng thanh toán.
        paid_at: Thời điểm thanh toán thành công.
        failed_at: Thời điểm thanh toán thất bại.
        failure_reason: Lý do thất bại.
        created_at: Thời điểm tạo.
        updated_at: Thời điểm cập nhật.
    """
    id: UUID
    booking_id: UUID
    transaction_id: str | None
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus
    payment_url: str | None
    callback_data: dict[str, Any] = Field(default_factory=dict)
    paid_at: datetime | None
    failed_at: datetime | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime


class PaymentWithBooking(PaymentDTO):
    """Payment kèm thông tin booking.
    
    Dùng khi cần hiển thị payment cùng thông tin booking liên quan.
    
    Attributes:
        booking: Thông tin cơ bản về booking.
    """
    booking: BookingBasic


class PaymentSearchCriteria(BaseSchema):
    """Tiêu chí tìm kiếm payment.
    
    Dùng trong service layer để filter payments.
    
    Attributes:
        booking_id: Lọc theo booking.
        status: Lọc theo trạng thái thanh toán.
        payment_method: Lọc theo phương thức thanh toán.
        transaction_id: Tìm theo mã giao dịch.
        date_from: Lọc từ ngày.
        date_to: Lọc đến ngày.
    """
    booking_id: UUID | None = Field(None, description="Lọc theo booking")
    status: PaymentStatus | None = Field(None, description="Lọc theo trạng thái")
    payment_method: PaymentMethod | None = Field(None, description="Lọc theo phương thức")
    transaction_id: str | None = Field(None, description="Tìm theo mã giao dịch")
    date_from: datetime | None = Field(None, description="Từ ngày")
    date_to: datetime | None = Field(None, description="Đến ngày")


class PaymentStatusUpdate(BaseSchema):
    """Schema cập nhật trạng thái payment.
    
    Dùng trong service layer để cập nhật payment sau khi
    nhận callback từ cổng thanh toán.
    
    Attributes:
        payment_id: ID payment cần cập nhật.
        new_status: Trạng thái mới.
        transaction_id: Mã giao dịch từ cổng thanh toán.
        failure_reason: Lý do thất bại (nếu failed).
        callback_data: Dữ liệu callback raw từ cổng thanh toán.
    """
    payment_id: UUID
    new_status: PaymentStatus
    transaction_id: str | None = None
    failure_reason: str | None = None
    callback_data: dict[str, Any] | None = None


class VNPayCallbackData(BaseSchema):
    """Schema cho callback từ VNPay.
    
    Parse dữ liệu callback từ VNPay sau khi user thanh toán.
    
    Attributes:
        vnp_TmnCode: Mã website merchant.
        vnp_Amount: Số tiền × 100 (VNPay format).
        vnp_BankCode: Mã ngân hàng.
        vnp_BankTranNo: Mã giao dịch ngân hàng.
        vnp_CardType: Loại thẻ.
        vnp_PayDate: Thời gian thanh toán.
        vnp_OrderInfo: Thông tin đơn hàng.
        vnp_TransactionNo: Mã giao dịch VNPay.
        vnp_ResponseCode: Mã phản hồi (00 = thành công).
        vnp_TransactionStatus: Trạng thái giao dịch.
        vnp_TxnRef: Mã đơn hàng merchant.
        vnp_SecureHash: Chữ ký để verify.
    """
    vnp_TmnCode: str = Field(..., description="Mã website merchant")
    vnp_Amount: int = Field(..., description="Số tiền * 100")
    vnp_BankCode: str | None = Field(None, description="Mã ngân hàng")
    vnp_BankTranNo: str | None = Field(None, description="Mã giao dịch ngân hàng")
    vnp_CardType: str | None = Field(None, description="Loại thẻ")
    vnp_PayDate: str | None = Field(None, description="Thời gian thanh toán")
    vnp_OrderInfo: str = Field(..., description="Thông tin đơn hàng")
    vnp_TransactionNo: str | None = Field(None, description="Mã giao dịch VNPay")
    vnp_ResponseCode: str = Field(..., description="Mã phản hồi")
    vnp_TransactionStatus: str = Field(..., description="Trạng thái giao dịch")
    vnp_TxnRef: str = Field(..., description="Mã đơn hàng merchant")
    vnp_SecureHash: str = Field(..., description="Chữ ký")


class MomoCallbackData(BaseSchema):
    """Schema cho callback từ Momo.
    
    Parse dữ liệu callback từ Momo sau khi user thanh toán.
    
    Attributes:
        partnerCode: Mã đối tác.
        orderId: Mã đơn hàng.
        requestId: Mã request.
        amount: Số tiền.
        orderInfo: Thông tin đơn hàng.
        orderType: Loại đơn hàng.
        transId: Mã giao dịch Momo.
        resultCode: Mã kết quả (0 = thành công).
        message: Thông điệp từ Momo.
        payType: Phương thức thanh toán.
        responseTime: Thời gian phản hồi (timestamp).
        extraData: Dữ liệu thêm.
        signature: Chữ ký để verify.
    """
    partnerCode: str = Field(..., description="Mã đối tác")
    orderId: str = Field(..., description="Mã đơn hàng")
    requestId: str = Field(..., description="Mã request")
    amount: int = Field(..., description="Số tiền")
    orderInfo: str = Field(..., description="Thông tin đơn hàng")
    orderType: str = Field(..., description="Loại đơn hàng")
    transId: int = Field(..., description="Mã giao dịch Momo")
    resultCode: int = Field(..., description="Mã kết quả")
    message: str = Field(..., description="Thông điệp")
    payType: str = Field(..., description="Phương thức thanh toán")
    responseTime: int = Field(..., description="Thời gian phản hồi (timestamp)")
    extraData: str | None = Field(None, description="Dữ liệu thêm")
    signature: str = Field(..., description="Chữ ký")


class PaymentResult(BaseSchema):
    """Kết quả xử lý thanh toán.
    
    Trả về sau khi service xử lý callback từ cổng thanh toán.
    
    Attributes:
        success: Thanh toán thành công không.
        payment_id: ID payment (nếu có).
        transaction_id: Mã giao dịch từ cổng thanh toán.
        status: Trạng thái payment sau xử lý.
        message: Thông báo kết quả.
        payment_url: URL redirect (nếu cần redirect tiếp).
    """
    success: bool
    payment_id: UUID | None = None
    transaction_id: str | None = None
    status: PaymentStatus
    message: str
    payment_url: str | None = None
