class AppException(Exception):
    """Base exception cho toàn bộ exception"""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        details: dict | None = None
    ):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    status_code: int = 404
    error_code: str = "NOT_FOUND"

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict | None = None
    ):
        super().__init__(message, details)


class ValidationError(AppException):
    status_code: int = 422
    error_code: str = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str = "Validation failed",
        details: dict | None = None
    ):
        super().__init__(message, details)


class ConflictError(AppException):
    status_code: int = 409
    error_code: str = "CONFLICT"

    def __init__(
        self,
        message: str = "Resource already exists",
        details: dict | None = None
    ):
        super().__init__(message, details)


class UnauthorizedError(AppException):
    status_code: int = 401
    error_code: str = "UNAUTHORIZED"

    def __init__(
        self,
        message: str = "Authentication required",
        details: dict | None = None
    ):
        super().__init__(message, details)


class ForbiddenError(AppException):
    status_code: int = 403
    error_code: str = "FORBIDDEN"

    def __init__(
        self,
        message: str = "Permission denied",
        details: dict | None = None
    ):
        super().__init__(message, details)


class BadRequestError(AppException):
    status_code: int = 400
    error_code: str = "BAD_REQUEST"

    def __init__(
        self,
        message: str = "Invalid request",
        details: dict | None = None
    ):
        super().__init__(message, details)
