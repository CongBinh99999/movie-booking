from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Text, text, CheckConstraint, UniqueConstraint, Index
from sqlalchemy import Enum as SAEnum, Numeric
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from app.modules.auth.models import Users
    from app.modules.showtimes.models import Showtimes
    from app.modules.cinemas.models import Seats
    from app.modules.payments.models import Payments


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BookingSeats(SQLModel, table=True):
    __tablename__ = "booking_seats"  # type: ignore[assignment]
    __table_args__ = (
        UniqueConstraint("booking_id", "seat_id",
                         name="uq_booking_seats_booking_seat"),
        CheckConstraint("price >= 0", name="ck_booking_seats_price_positive"),
        Index("idx_booking_seats_booking_id", "booking_id"),
        Index("idx_booking_seats_seat_id", "seat_id")
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    seat_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("seats.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    price: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2), nullable=False
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)")
        )
    )


class Bookings(SQLModel, table=True):
    __tablename__ = "bookings"  # type: ignore[assignment]
    __table_args__ = (
        Index("idx_bookings_user_id", "user_id"),
        Index("idx_bookings_showtime_id", "showtime_id"),
        Index("idx_bookings_booking_code", "booking_code"),
        Index("idx_bookings_status", "status"),
        Index("idx_bookings_expires_at", "expires_at"),


        Index(
            "idx_bookings_pending_expires",
            "status",
            "expires_at",
            postgresql_where=text("status = 'pending'")
        ),


        CheckConstraint("total_amount >= 0",
                        name="ck_bookings_total_amount_positive"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False
        )
    )

    showtime_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("showtimes.id", ondelete="CASCADE"),
            nullable=False
        )
    )

    booking_code: str = Field(max_length=20, nullable=False, unique=True)

    status: BookingStatus = Field(
        sa_column=Column(
            SAEnum(
                BookingStatus,
                name="booking_status",
                create_type=False,
                native_enum=True
            ),
            nullable=False,
            default=BookingStatus.PENDING
        )
    )

    total_amount: Decimal = Field(
        sa_column=Column(Numeric(12, 2), nullable=False)
    )

    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False
        )
    )

    confirmed_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=None
        )
    )

    cancelled_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=None
        )
    )

    cancellation_reason: str | None = Field(default=None, sa_type=Text)

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

    # relationships
    user: "Users" = Relationship(
        back_populates="bookings"
    )
    showtime: "Showtimes" = Relationship(
        back_populates="bookings"
    )
    seats: list["Seats"] = Relationship(
        back_populates="bookings",
        link_model=BookingSeats
    )
    payments: list["Payments"] = Relationship(
        back_populates="booking"
    )
