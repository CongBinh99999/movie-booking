from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text, Column, ForeignKey, Numeric, Enum as SAEnum, Text, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.types import DateTime

from uuid import uuid4, UUID
from typing import TYPE_CHECKING, Any
from enum import Enum
from datetime import timezone, datetime
from decimal import Decimal


if TYPE_CHECKING:
    from app.modules.bookings.models import Bookings


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    VNPAY = "vnpay"
    MOMO = "momo"
    ZALOPAY = "zalopay"


class Payments(SQLModel, table=True):
    __tablename__ = "payments"  # type: ignore[assigment]
    __table_args__ = (
        # check constraint
        CheckConstraint("amount > 0", "ck_payments_amount_positive"),


        # index constraint
        Index("idx_payments_booking_id", "booking_id"),
        Index("idx_payments_transaction_id", "transaction_id"),
        Index("idx_payments_status", "status"),
        Index("idx_payments_payment_method", "payment_method")
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    transaction_id: str | None = Field(
        default=None, max_length=100, unique=True)
    payment_method: PaymentMethod = Field(
        sa_column=Column(
            SAEnum(
                PaymentMethod,
                name="payment_method",
                create_type=False,
                native_enum=True
            ),
            nullable=False
        )
    )
    amount: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False
        )
    )
    status: PaymentStatus = Field(
        sa_column=Column(
            SAEnum(
                PaymentStatus,
                name="payment_status",
                create_type=False,
                native_enum=True
            ),
            nullable=False,
            default=PaymentStatus.PENDING
        )
    )
    payment_url: str | None = Field(default=None, sa_type=Text)
    callback_data: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(
            JSONB,
            nullable=False,
            server_default=text("'{}'::jsonb")
        )
    )
    paid_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True)
        ),
        default=None
    )
    failed_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True)
        ),
        default=None
    )
    failure_reason: str | None = Field(default=None, sa_type=Text)
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
    booking: "Bookings" = Relationship(
        back_populates="payments"
    )
