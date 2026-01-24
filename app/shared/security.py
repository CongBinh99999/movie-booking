"""Security utilities for password hashing and JWT.

TODO: Implement:
- hash_password(password: str) -> str (bcrypt)
- verify_password(plain: str, hashed: str) -> bool
- create_access_token(subject: str, expires_delta?) -> str
- create_refresh_token(subject: str, expires_delta?) -> str
- decode_token(token: str) -> dict

Use settings from app.core.config for:
- JWT_SECRET_KEY
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- REFRESH_TOKEN_EXPIRE_DAYS
"""

# TODO: Implement security utilities
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_setting
