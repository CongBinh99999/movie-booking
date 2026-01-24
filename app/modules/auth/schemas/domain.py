from pydantic import EmailStr, ConfigDict
from app.modules.auth.models import RoleType
from uuid import UUID
from datetime import datetime

from app.shared.schemas.base import BaseSchema, TimeStampMixin, IdentifiableMixin


class UserCreate(BaseSchema):
    email: EmailStr
    username: str
    hashed_password: str
    full_name: str | None = None
    role: RoleType = RoleType.USER


class UserUpdate(BaseSchema):
    email: EmailStr | None = None
    full_name: str | None = None


class TokenPayload(BaseSchema):
    model_config = ConfigDict(
        **BaseSchema.model_config.__dict__,
        frozen=True
    )
    sub: UUID
    role: str
    exp: datetime
    type: str


class UserDTO(BaseSchema, IdentifiableMixin, TimeStampMixin): 
    email: str 
    username: str 
    hashed_password: str 
    full_name: str | None = None 
    role: RoleType
    is_active: bool


class UserSearchCriteria(BaseSchema): 
    role: RoleType | None = None 
    username: str | None = None
    email: str | None = None 
    full_name: str | None = None 
    is_active: bool | None = None 


