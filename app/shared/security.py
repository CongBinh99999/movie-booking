"""Các tiện ích bảo mật cho mã hóa mật khẩu và JWT.

Sử dụng argon2 để mã hóa mật khẩu và jose cho các thao tác JWT.

Cấu hình từ app.core.config:
- JWT_SECRET
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- REFRESH_TOKEN_EXPIRE_DAYS
"""


from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import uuid4, UUID

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_setting
from app.modules.auth.schemas.domain import TokenPayload

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

settings = get_setting()


def hash_password(password: str) -> str:
    """Mã hóa mật khẩu sử dụng argon2.

    Args:
        password: Mật khẩu dạng văn bản thuần cần mã hóa.

    Returns:
        Chuỗi mật khẩu đã được mã hóa.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
    """Xác thực mật khẩu và tự động re-hash nếu thuật toán đã deprecated.

    Hàm này kiểm tra mật khẩu và nếu hash hiện tại sử dụng thuật toán
    deprecated (ví dụ: bcrypt khi đã chuyển sang argon2), sẽ trả về hash mới
    để caller cập nhật vào database.

    Args:
        plain_password: Mật khẩu dạng văn bản thuần cần xác thực.
        hashed_password: Mật khẩu đã mã hóa để so sánh.

    Returns:
        Tuple gồm:
        - bool: True nếu mật khẩu khớp, False nếu không khớp.
        - str | None: Hash mới nếu cần cập nhật, None nếu không cần.
    """
    is_valid, new_hash = pwd_context.verify_and_update(
        plain_password, hashed_password)
    return is_valid, new_hash


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
    jti: str | None = None
) -> tuple[str, str, datetime]:
    """Tạo JWT token với các tham số được chỉ định.

    Args:
        subject: Chủ thể (thường là user ID) cho token.
        token_type: Loại token ('access' hoặc 'refresh').
        expires_delta: Khoảng thời gian hết hạn tùy chỉnh (tùy chọn).
        extra_claims: Các claims bổ sung để đưa vào token (tùy chọn).
        jti: JWT ID (tùy chọn). Nếu không cung cấp, UUID sẽ được tạo tự động.

    Returns:
        Tuple chứa (chuỗi_token, jti, thời_gian_hết_hạn).
    """
    token_jti = jti if jti else str(uuid4())
    now = datetime.now(timezone.utc)

    if expires_delta:
        expires_at = now + expires_delta
    elif token_type == "access":
        expires_at = now + \
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": subject,
        "type": token_type,
        "jti": token_jti,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp())
    }

    if extra_claims:
        for key, value in extra_claims.items():
            if value is not None:
                payload[key] = str(value) if isinstance(value, UUID) else value

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM
    )

    return token, token_jti, expires_at


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> tuple[str, str, datetime]:
    """Tạo access token cho chủ thể được chỉ định.

    Args:
        subject: Chủ thể (thường là user ID) cho token.
        extra_claims: Các claims bổ sung để đưa vào token (tùy chọn).

    Returns:
        Tuple chứa (chuỗi_token, jti, thời_gian_hết_hạn).
    """
    return create_token(subject=subject, token_type="access", extra_claims=extra_claims)


def create_refresh_token(subject: str, extra_claims: dict[str, Any] | None = None) -> tuple[str, str, datetime]:
    """Tạo refresh token cho chủ thể được chỉ định.

    Args:
        subject: Chủ thể (thường là user ID) cho token.
        extra_claims: Các claims bổ sung để đưa vào token (tùy chọn).

    Returns:
        Tuple chứa (chuỗi_token, jti, thời_gian_hết_hạn).
    """
    return create_token(subject=subject, token_type="refresh", extra_claims=extra_claims)


def decode_token(token: str) -> TokenPayload:
    """Giải mã và xác thực JWT token.

    Args:
        token: Chuỗi JWT token cần giải mã.

    Returns:
        Đối tượng TokenPayload chứa dữ liệu token đã giải mã.

    Raises:
        jose.JWTError: Nếu token không hợp lệ hoặc đã hết hạn.
    """
    data = jwt.decode(token, settings.JWT_SECRET,
                      algorithms=[settings.JWT_ALGORITHM])
    return TokenPayload.model_validate(data)
