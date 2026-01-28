from app.shared.exceptions import (
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError
)
from uuid import UUID


class InvalidCredentialsError(UnauthorizedError):
    error_code: str = "INVALID_CREDENTIALS_ERROR"

    def __init__(self, user_id: UUID | None = None):
        super().__init__(
            message="Invalid credentials",
            details={
                "user_id": str(user_id) if user_id else None
            }
        )


class InvalidTokenError(UnauthorizedError):
    error_code: str = "INVALID_TOKEN_ERROR"

    def __init__(self, reason: str = "Token is invalid or expired"):
        super().__init__(message=reason)


class TokenExpiredError(UnauthorizedError):
    error_code: str = "TOKEN_EXPIRED_ERROR"

    def __init__(self):
        super().__init__(message="Token has expired")


class TokenRevokedError(UnauthorizedError):
    error_code: str = "TOKEN_REVOKED_ERROR"

    def __init__(self):
        super().__init__(message="Token is revoked")


class InactiveUserError(ForbiddenError):
    error_code: str = "INACTIVE_USER_ERROR"

    def __init__(self):
        super().__init__(message="User account is inactive")


class InsufficientPermissionsError(ForbiddenError):
    error_code: str = "INSUFFICIENT_PERMISSIONS"

    def __init__(self, required_role: str | None = None):
        message = f"Required role: {required_role}" if required_role else "Insufficient permissions"
        super().__init__(message=message)


class EmailAlreadyExistsError(ConflictError):
    error_code: str = "EMAIL_ALREADY_EXISTS"

    def __init__(self, email: str | None = None):
        message = "Email already exists"
        details = {"email": email} if email else {}
        super().__init__(message=message, details=details)


class UsernameAlreadyExistsError(ConflictError):
    error_code: str = "USERNAME_ALREADY_EXISTS"

    def __init__(self, username: str | None = None):
        message = "Username already exists"
        details = {"username": username} if username else {}
        super().__init__(message=message, details=details)


class UserNotFoundError(NotFoundError):
    error_code: str = "USER_NOT_FOUND_ERROR"

    def __init__(self, user_id: UUID | None = None):
        details = {"user_id": str(user_id)} if user_id else {}
        super().__init__(message="User not found", details=details)
