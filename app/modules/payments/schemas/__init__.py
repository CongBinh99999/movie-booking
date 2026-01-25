"""Payments schemas package."""
from app.modules.payments.schemas.domain import (
    PaymentDTO,
    PaymentWithBooking,
    PaymentSearchCriteria,
    PaymentStatusUpdate,
    VNPayCallbackData,
    MomoCallbackData,
    PaymentResult,
)

from app.modules.payments.schemas.api import (
    PaymentCreateRequest,
    PaymentCallbackRequest,
    PaymentResponse,
    PaymentListResponse,
    RefundRequest,
    PaymentQueryParams,
)

__all__ = [
    # Domain schemas
    "PaymentDTO",
    "PaymentWithBooking",
    "PaymentSearchCriteria",
    "PaymentStatusUpdate",
    "VNPayCallbackData",
    "MomoCallbackData",
    "PaymentResult",
    # API schemas
    "PaymentCreateRequest",
    "PaymentCallbackRequest",
    "PaymentResponse",
    "PaymentListResponse",
    "RefundRequest",
    "PaymentQueryParams",
]
