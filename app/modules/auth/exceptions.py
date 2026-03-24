from uuid import UUID
from app.shared.exceptions import (
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError
)


class InvalidCredentialsError(UnauthorizedError):
    """Thông tin đăng nhập không hợp lệ."""
    
    error_code = "INVALID_CREDENTIALS"

    def __init__(self) -> None:
        super().__init__(message="Email hoặc mật khẩu không đúng")


class InvalidTokenError(UnauthorizedError):
    """Token không hợp lệ."""
    
    error_code = "INVALID_TOKEN"

    def __init__(self, reason: str | None = None) -> None:
        self.reason = reason
        
        super().__init__(
            message=reason or "Token không hợp lệ"
        )


class TokenExpiredError(UnauthorizedError):
    """Token đã hết hạn."""
    
    error_code = "TOKEN_EXPIRED"

    def __init__(self) -> None:
        super().__init__(message="Token đã hết hạn")


class TokenRevokedError(UnauthorizedError):
    """Token đã bị thu hồi."""
    
    error_code = "TOKEN_REVOKED"

    def __init__(self) -> None:
        super().__init__(message="Token đã bị thu hồi")


class InactiveUserError(ForbiddenError):
    """Tài khoản không hoạt động."""
    
    error_code = "INACTIVE_USER"

    def __init__(self) -> None:
        super().__init__(message="Tài khoản không hoạt động")


class InsufficientPermissionsError(ForbiddenError):
    """Không đủ quyền truy cập."""
    
    error_code = "INSUFFICIENT_PERMISSIONS"

    def __init__(self, required_role: str | None = None) -> None:
        self.required_role = required_role
        
        message = "Không đủ quyền truy cập"
        if required_role:
            message = f"Yêu cầu quyền: {required_role}"
        
        super().__init__(message=message)


class EmailAlreadyExistsError(ConflictError):
    """Email đã được đăng ký."""
    
    error_code = "EMAIL_ALREADY_EXISTS"

    def __init__(self, email: str | None = None) -> None:
        self.email = email
        
        super().__init__(
            message="Email đã tồn tại",
            details={"email": email} if email else None
        )


class UsernameAlreadyExistsError(ConflictError):
    """Tên người dùng đã tồn tại."""
    
    error_code = "USERNAME_ALREADY_EXISTS"

    def __init__(self, username: str | None = None) -> None:
        self.username = username
        
        super().__init__(
            message="Tên người dùng đã tồn tại",
            details={"username": username} if username else None
        )


class UserNotFoundError(NotFoundError):
    """Không tìm thấy người dùng."""
    
    error_code = "USER_NOT_FOUND"

    def __init__(self, user_id: UUID | None = None) -> None:
        self.user_id = user_id
        
        super().__init__(
            message="Không tìm thấy người dùng",
            details={"user_id": str(user_id)} if user_id else None
        )