from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.config import get_setting
from app.modules.payments.models import PaymentMethod, PaymentStatus
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas.domain import PaymentCreate
from app.modules.payments.exceptions import (
    PaymentNotFoundError,
    InvalidPaymentAmountError,
    InvalidPaymentSignatureError,
)
from app.modules.payments import vnpay_utils
from app.modules.bookings.service.booking_service import BookingService
from app.modules.bookings.exceptions import BookingNotFoundError, BookingOwnershipError


VNPAY_AMOUNT_MULTIPLIER = 100
TERMINAL_STATUSES = {PaymentStatus.COMPLETED, PaymentStatus.FAILED}


class PaymentService:
    """Business logic cho thanh toán VNPay."""

    def __init__(
        self,
        payment_repo: PaymentRepository,
        booking_service: BookingService,
    ) -> None:
        self.payment_repo = payment_repo
        self.booking_service = booking_service
        self._settings = get_setting()

    async def create_vnpay_payment(
        self,
        booking_id: UUID,
        user_id: UUID,
        client_ip: str,
    ) -> str:
        """Tạo payment record và trả về VNPay payment URL."""
        booking = await self.booking_service.get_booking_by_id(
            booking_id, user_id=user_id
        )

        vnpay_amount = int(booking.total_amount * VNPAY_AMOUNT_MULTIPLIER)

        payment = await self.payment_repo.create(
            PaymentCreate(
                booking_id=booking_id,
                amount=booking.total_amount,
                payment_method=PaymentMethod.VNPAY,
            )
        )

        payment_url = vnpay_utils.generate_payment_url(
            tmn_code=self._settings.VNPAY_TMN_CODE,
            hash_secret=self._settings.VNPAY_HASH_SECRET,
            payment_url_base=self._settings.VNPAY_PAYMENT_URL,
            txn_ref=str(payment.id),
            amount=vnpay_amount,
            order_info=f"Thanh toan ve xem phim booking {booking_id}",
            return_url=self._settings.VNPAY_RETURN_URL,
            ip_addr=client_ip,
        )

        await self.payment_repo.update(payment, data=_url_update(payment_url))

        return payment_url

    async def process_vnpay_ipn(self, query_params: dict) -> dict:
        """Xử lý IPN Webhook từ VNPay (server-to-server)"""
        if not vnpay_utils.verify_secure_hash(query_params, self._settings.VNPAY_HASH_SECRET):
            return {"RspCode": "97", "Message": "Invalid Signature"}

        txn_ref = query_params.get("vnp_TxnRef", "")
        try:
            payment_id = UUID(txn_ref)
        except ValueError:
            return {"RspCode": "01", "Message": "Order Not Found"}

        payment = await self.payment_repo.get_by_id(payment_id)
        if payment is None:
            return {"RspCode": "01", "Message": "Order Not Found"}

        vnpay_amount_raw = int(query_params.get("vnp_Amount", 0))
        expected_amount = int(payment.amount * VNPAY_AMOUNT_MULTIPLIER)
        if vnpay_amount_raw != expected_amount:
            return {"RspCode": "04", "Message": "Invalid Amount"}

        if payment.status in TERMINAL_STATUSES:
            return {"RspCode": "02", "Message": "Order already confirmed"}

        response_code = query_params.get("vnp_ResponseCode", "")
        transaction_no = query_params.get("vnp_TransactionNo", "")

        if response_code == "00":
            await self.payment_repo.mark_as_completed(
                payment,
                transaction_id=transaction_no,
                callback_data=query_params,
            )
            await self.booking_service.confirm_booking(
                booking_id=payment.booking_id,
                user_id=(await self._get_booking_user_id(payment.booking_id)),
            )
        else:
            await self.payment_repo.mark_as_failed(
                payment,
                reason=f"VNPay ResponseCode={response_code}",
            )

        return {"RspCode": "00", "Message": "Confirm Success"}

    async def verify_vnpay_return(self, query_params: dict) -> dict:
        """Verify chữ ký VNPay Return URL"""
        if not vnpay_utils.verify_secure_hash(query_params, self._settings.VNPAY_HASH_SECRET):
            return {"is_valid": False, "is_success": False}

        is_success = query_params.get("vnp_ResponseCode", "") == "00"
        return {"is_valid": True, "is_success": is_success}

    async def _get_booking_user_id(self, booking_id: UUID) -> UUID:
        booking = await self.booking_service.get_booking_by_id(booking_id)
        return booking.user_id


def _url_update(payment_url: str):
    from app.modules.payments.schemas.domain import PaymentUpdate
    return PaymentUpdate(payment_url=payment_url)


def get_payment_service(
    payment_repo: "PaymentRepoDeps",
    booking_service: "BookingServiceDep",
) -> PaymentService:
    return PaymentService(payment_repo=payment_repo, booking_service=booking_service)


from app.modules.payments.repository import PaymentRepoDeps  # noqa: E402
from app.modules.bookings.service import BookingServiceDep  # noqa: E402

PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
