from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import Enum as SAEnum, Index, text
from sqlalchemy.types import DateTime
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from enum import Enum


if TYPE_CHECKING:
    from app.modules.bookings.models import Bookings


class RoleType(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Users(SQLModel, table=True):
    __tablename__ = "users" #type: ignore[assigment]
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_role", "role")
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, nullable=False, unique=True)
    username: str = Field(max_length=100, nullable=False, unique=True)
    hashed_password: str = Field(max_length=255, nullable=False)
    full_name: str | None = Field(default=None, max_length=255)
    role: RoleType = Field(
        sa_column=Column(
            SAEnum(
                RoleType,
                name="user_role",
                create_type=False,
                native_enum=True
            ),
            nullable=False,
            default=RoleType.USER
        )
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)")
        )
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            onupdate=lambda: datetime.now(timezone.utc)
        )
    )

    
    #relationships
    bookings: list["Bookings"] = Relationship(
        back_populates="user", 
    )
    
