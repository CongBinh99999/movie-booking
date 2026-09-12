"""Regression test cho luồng thanh toán VNPay."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.modules.bookings.exceptions import BookingExpiredError
from app.modules.bookings.models import BookingStatus
from app.modules.payments import vnpay_utils
from app.modules.payments.models import PaymentStatus
from app.modules.payments.service import PaymentService

SECRET = "test-hash-secret"


# --- chữ ký ---

def test_ky_theo_dung_encoding_cua_vnpay():
    """VNPay dùng quote_plus: dấu cách phải thành '+', không phải '%20'."""
    params = {"vnp_OrderInfo": "Thanh toan ve xem phim", "vnp_Amount": "10000"}
    assert "+" in vnpay_utils._build_query_string(params)
    assert "%20" not in vnpay_utils._build_query_string(params)


def test_verify_chu_ky_khop_voi_url_da_sinh():
    from urllib.parse import parse_qsl, urlparse

    url = vnpay_utils.generate_payment_url(
        tmn_code="TMN", hash_secret=SECRET,
        payment_url_base="https://sandbox.vnpayment.vn/pay",
        txn_ref=str(uuid4()), amount=1000000,
        order_info="Thanh toan ve xem phim booking abc",
        return_url="http://localhost:3000/payment/result", ip_addr="127.0.0.1",
    )
    params = dict(parse_qsl(urlparse(url).query))
    assert vnpay_utils.verify_secure_hash(params, SECRET)


# --- IPN ---

def make_service(booking, payment, confirm_error=None):
    calls = {"completed": None, "failed": None, "confirmed": False}

    async def mark_as_completed(p, transaction_id, callback_data):
        calls["completed"] = callback_data
        p.status = PaymentStatus.COMPLETED

    async def mark_as_failed(p, reason):
        calls["failed"] = reason

    async def confirm_booking(booking_id, user_id):
        if confirm_error:
            raise confirm_error
        calls["confirmed"] = True

    service = PaymentService.__new__(PaymentService)
    service.payment_repo = SimpleNamespace(
        get_by_id=_ret(payment),
        mark_as_completed=mark_as_completed,
        mark_as_failed=mark_as_failed,
    )
    service.booking_service = SimpleNamespace(
        get_booking_by_id=_ret(booking), confirm_booking=confirm_booking
    )
    service._settings = SimpleNamespace(VNPAY_HASH_SECRET=SECRET)
    return service, calls


def _ret(value):
    async def _f(*a, **k):
        return value
    return _f


def signed(params: dict) -> dict:
    out = dict(params)
    out["vnp_SecureHash"] = vnpay_utils._sign(
        vnpay_utils._build_query_string(out), SECRET
    )
    return out


def make_pair(booking_status=BookingStatus.PENDING):
    payment = SimpleNamespace(
        id=uuid4(), booking_id=uuid4(),
        amount=Decimal("100000"), status=PaymentStatus.PENDING,
    )
    booking = SimpleNamespace(
        id=payment.booking_id, user_id=uuid4(), status=booking_status,
        total_amount=Decimal("100000"),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    return booking, payment


@pytest.mark.asyncio
async def test_ipn_thanh_cong_xac_nhan_booking_va_ghi_nhan_payment():
    booking, payment = make_pair()
    service, calls = make_service(booking, payment)

    result = await service.process_vnpay_ipn(signed({
        "vnp_TxnRef": str(payment.id), "vnp_Amount": "10000000",
        "vnp_ResponseCode": "00", "vnp_TransactionNo": "123",
    }))

    assert result["RspCode"] == "00"
    assert calls["confirmed"]
    assert "_needs_refund" not in calls["completed"]


@pytest.mark.asyncio
async def test_booking_het_han_khong_lam_ipn_no_va_danh_dau_can_hoan_tien():
    """Trước đây BookingExpiredError bay lên -> IPN trả 500, VNPay retry,
    payment đã COMPLETED nên lần sau trả RspCode 02. Tiền mất, vé không có."""
    booking, payment = make_pair(booking_status=BookingStatus.EXPIRED)
    service, calls = make_service(
        booking, payment,
        confirm_error=BookingExpiredError(booking.id, booking.expires_at),
    )

    result = await service.process_vnpay_ipn(signed({
        "vnp_TxnRef": str(payment.id), "vnp_Amount": "10000000",
        "vnp_ResponseCode": "00", "vnp_TransactionNo": "123",
    }))

    assert result["RspCode"] == "00"          # VNPay ngừng retry
    assert calls["completed"]["_needs_refund"] is True
    assert calls["completed"]["_booking_status"] == "expired"


@pytest.mark.asyncio
async def test_chu_ky_sai_bi_tu_choi():
    booking, payment = make_pair()
    service, _ = make_service(booking, payment)

    result = await service.process_vnpay_ipn({
        "vnp_TxnRef": str(payment.id), "vnp_Amount": "10000000",
        "vnp_ResponseCode": "00", "vnp_SecureHash": "deadbeef",
    })
    assert result["RspCode"] == "97"


@pytest.mark.asyncio
async def test_vnp_amount_khong_phai_so_khong_lam_no_500():
    booking, payment = make_pair()
    service, _ = make_service(booking, payment)

    result = await service.process_vnpay_ipn(signed({
        "vnp_TxnRef": str(payment.id), "vnp_Amount": "abc",
        "vnp_ResponseCode": "00",
    }))
    assert result["RspCode"] == "04"


@pytest.mark.asyncio
async def test_khong_tao_duoc_link_thanh_toan_cho_booking_het_han():
    booking, payment = make_pair()
    booking.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    service, _ = make_service(booking, payment)

    with pytest.raises(BookingExpiredError):
        await service.create_vnpay_payment(
            booking_id=booking.id, user_id=booking.user_id, client_ip="127.0.0.1"
        )
