from uuid import UUID
from decimal import Decimal
from app.shared.exceptions import NotFoundError, BadRequestError


class PaymentNotFoundError(NotFoundError):
    """Không tìm thấy thông tin thanh toán."""

    error_code = "PAYMENT_NOT_FOUND"

    def __init__(self, payment_id: UUID | None = None, transaction_id: UUID | None = None) -> None:
        self.payment_id = payment_id
        self.transaction_id = transaction_id

        details: dict[str, str] = {}
        if payment_id is not None:
            details["payment_id"] = str(payment_id)
        if transaction_id is not None:
            details["transaction_id"] = str(transaction_id)

        super().__init__(
            message="Không tìm thấy thông tin thanh toán",
            details=details if details else None
        )


class PaymentAlreadyCompletedError(BadRequestError):
    """Thanh toán đã được hoàn thành."""

    error_code = "PAYMENT_ALREADY_COMPLETED"

    def __init__(self, payment_id: UUID) -> None:
        self.payment_id = payment_id

        super().__init__(
            message="Thanh toán này đã được hoàn thành trước đó",
            details={"payment_id": str(payment_id)}
        )


class PaymentAlreadyFailedError(BadRequestError):
    """Thanh toán đã thất bại."""

    error_code = "PAYMENT_ALREADY_FAILED"

    def __init__(self, payment_id: UUID) -> None:
        self.payment_id = payment_id

        super().__init__(
            message="Thanh toán này đã thất bại trước đó",
            details={"payment_id": str(payment_id)}
        )


class PaymentExpiredError(BadRequestError):
    """Phiên thanh toán đã hết hạn."""

    error_code = "PAYMENT_EXPIRED"

    def __init__(self, payment_id: UUID) -> None:
        self.payment_id = payment_id

        super().__init__(
            message="Phiên thanh toán đã hết hạn",
            details={"payment_id": str(payment_id)}
        )


class InvalidPaymentAmountError(BadRequestError):
    """Số tiền thanh toán không khớp."""

    error_code = "INVALID_PAYMENT_AMOUNT"

    def __init__(self, expected: Decimal, received: Decimal) -> None:
        self.expected = expected
        self.received = received

        super().__init__(
            message="Số tiền thanh toán không khớp",
            details={
                "expected": str(expected),
                "received": str(received)
            }
        )


class PaymentGatewayError(BadRequestError):
    """Lỗi từ cổng thanh toán (VNPay, MoMo, ZaloPay...)."""

    error_code = "PAYMENT_GATEWAY_ERROR"

    def __init__(
        self,
        gateway: str,
        gateway_error_code: str | None = None,
        error_message: str | None = None
    ) -> None:
        self.gateway = gateway
        self.gateway_error_code = gateway_error_code
        self.error_message = error_message

        details: dict[str, str] = {"gateway": gateway}
        if gateway_error_code:
            details["gateway_error_code"] = gateway_error_code
        if error_message:
            details["gateway_error_message"] = error_message

        super().__init__(
            message=f"Lỗi cổng thanh toán: {error_message or gateway}",
            details=details
        )


class InvalidPaymentSignatureError(BadRequestError):
    """Chữ ký xác thực thanh toán không hợp lệ."""

    error_code = "INVALID_PAYMENT_SIGNATURE"

    def __init__(self, gateway: str) -> None:
        self.gateway = gateway

        super().__init__(
            message="Chữ ký xác thực thanh toán không hợp lệ",
            details={"gateway": gateway}
        )


class RefundNotAllowedError(BadRequestError):
    """Không thể hoàn tiền."""

    error_code = "REFUND_NOT_ALLOWED"

    def __init__(self, payment_id: UUID, reason: str) -> None:
        self.payment_id = payment_id
        self.reason = reason

        super().__init__(
            message=f"Không thể hoàn tiền: {reason}",
            details={
                "payment_id": str(payment_id),
                "reason": reason
            }
        )
