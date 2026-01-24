"""Shared utilities and common components.

TODO: Export from this package:
- Base, get_db from database
- Exception classes from exceptions
"""

# TODO: Add exports after implementing
from app.shared.exceptions import (
    AppException,
    NotFoundError,
    ValidationError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    BadRequestError
)

from app.shared.database import get_db


__all__ = [

    #Database
    "get_db", 

    #Exceptions
    "AppException",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "BadRequestError",
]
