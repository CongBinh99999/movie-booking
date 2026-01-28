from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict
from uuid import UUID
from datetime import datetime
import re

from app.shared.schemas.base import BaseRequest, BaseResponse, TimeStampMixin
from app.shared.schemas.pagination import PaginationResponse
from app.shared.schemas.nested import UserBasic
from app.modules.auth.models import RoleType


class RegisterRequest(BaseRequest):
    email: EmailStr = Field(..., min_length=3, max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=255)
    confirmed_password: str = Field(..., min_length=8, max_length=255)
    full_name: str | None = Field(default=None, min_length=5, max_length=255)

    @field_validator("username")
    @classmethod
    def valiate_username(cls, value: str) -> str:

        if len(value) < 3 or len(value) > 100:
            raise ValueError(
                "username không hợp lệ, có ít nhất 3 ký tự và dưới 100 ký tự")

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", value):
            raise ValueError(
                "username phải bắt đầu bằng chữ cái",
                "chỉ chứa chữ cái, số và underscore"
            )

        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password phải chứa ít nhất một chữ hoa")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password phải chứa ít nhất một chữ thường")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password phải có chứa ít nhất một số")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password phải chứa ít nhất một ký tự đặt biệt")

        return value

    @field_validator("full_name")
    @classmethod
    def validate_fullname(cls, value: str | None) -> str | None:
        if value is not None and value.strip() == "":
            raise ValueError("Không được là chuỗi rỗng")

        return value

    @model_validator(mode="after")
    def validate_password_match(self) -> "RegisterRequest":
        if self.password != self.confirmed_password:
            raise ValueError("Password và Confirmed Password không khớp")

        return self


class LoginRequest(BaseRequest):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=255)


class TokenResponse(BaseResponse):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
    token_type: str = Field(default="bearer")
    expires_at: datetime | None = Field(default=None)


class RefreshTokenRequest(BaseRequest):
    refresh_token: str = Field(...)


class UserResponse(BaseResponse, TimeStampMixin):
    id: UUID = Field(...)
    full_name: str | None = Field(default=None)
    is_active: bool = Field(default=True)


class UpdateProfileRequest(BaseRequest):
    email: str | None = None 
    full_name: str | None = None 


class ChangePasswordRequest(BaseRequest):
    old_password: str
    new_password: str 
    confirmed_new_password: str 


    @model_validator(mode="after")
    def validate_password_match(self) -> "ChangePasswordRequest": 
        if self.new_password != self.confirmed_new_password:
            raise ValueError(
                "new_password và confirmed_new_password không khớp")
        return self

    
class UserListResponse(PaginationResponse[UserBasic]): 
    pass 


class AdminUpdateUserRequest(UpdateProfileRequest):
    role: RoleType | None = None
    is_active: bool | None = None 


class LogoutRequest(BaseRequest): 
    access_token: str 
    refresh_token: str | None = None 

    @model_validator(mode="after")
    def at_least_one_token(self) -> "LogoutRequest": 
        if not self.access_token and not self.refresh_token:
            raise ValueError("Phải cung cấp ít nhất 1 trong 2 token")
        return self 
