import hmac
import hashlib
import urllib.parse
from datetime import datetime, timedelta, timezone

# VNPay quy định vnp_CreateDate và vnp_ExpireDate theo GMT+7, không phải UTC.
# Gửi giờ UTC thì mốc lệch 7 tiếng: cổng coi giao dịch là của quá khứ.
VN_TZ = timezone(timedelta(hours=7))


def _vnp_time(value: datetime) -> str:
    """Đổi sang giờ GMT+7, định dạng yyyyMMddHHmmss."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(VN_TZ).strftime("%Y%m%d%H%M%S")


def _build_query_string(params: dict) -> str:
    # VNPay 2.1.0 ký trên chuỗi encode bằng quote_plus (dấu cách -> "+"),
    # đúng mặc định của urlencode. Dùng quote (dấu cách -> "%20") sẽ ra chữ ký
    # khác với phía VNPay ngay khi có tham số chứa dấu cách, ví dụ vnp_OrderInfo.
    sorted_params = sorted(params.items())
    return urllib.parse.urlencode(sorted_params)


def _sign(data: str, secret_key: str) -> str:
    return hmac.new(
        secret_key.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def generate_payment_url(
    *,
    tmn_code: str,
    hash_secret: str,
    payment_url_base: str,
    txn_ref: str,
    amount: int,
    order_info: str,
    return_url: str,
    ip_addr: str,
    expire_at: datetime,
    created_at: datetime | None = None,
    locale: str = "vn",
    currency_code: str = "VND",
    order_type: str = "other",
) -> str:
    """Build VNPay payment URL với chữ ký HMAC-SHA512.

    amount phải nhân 100 trước khi truyền vào (quy định VNPay).

    expire_at nên lấy đúng hạn giữ ghế của booking: để VNPay hết hạn muộn hơn
    thì khách trả tiền xong mà ghế đã bị thả cho người khác.
    """
    created_at = created_at or datetime.now(timezone.utc)
    params: dict[str, str] = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": tmn_code,
        "vnp_Amount": str(amount),
        "vnp_CurrCode": currency_code,
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": order_info,
        "vnp_OrderType": order_type,
        "vnp_Locale": locale,
        "vnp_ReturnUrl": return_url,
        "vnp_IpAddr": ip_addr,
        "vnp_CreateDate": _vnp_time(created_at),
        # Bắt buộc ở 2.1.0. Thiếu nó cổng từ chối giao dịch.
        "vnp_ExpireDate": _vnp_time(expire_at),
    }

    query_string = _build_query_string(params)
    secure_hash = _sign(query_string, hash_secret)
    return f"{payment_url_base}?{query_string}&vnp_SecureHash={secure_hash}"


def verify_secure_hash(params: dict, hash_secret: str) -> bool:
    """Kiểm tra chữ ký HMAC-SHA512 từ VNPay callback."""
    received_hash = params.get("vnp_SecureHash", "")
    filtered = {
        k: v for k, v in params.items()
        if k not in ("vnp_SecureHash", "vnp_SecureHashType")
    }
    expected_hash = _sign(_build_query_string(filtered), hash_secret)
    return hmac.compare_digest(expected_hash.lower(), received_hash.lower())
