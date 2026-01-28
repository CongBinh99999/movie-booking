from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    text,
    Numeric,
    Enum as SAEnum,
    Text,
    Column,
    Index,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    CHAR
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import DateTime

from uuid import uuid4, UUID
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum
from decimal import Decimal

if TYPE_CHECKING:
    from app.modules.showtimes.models import Showtimes
    from app.modules.bookings.models import Bookings, BookingSeats


class SeatType(str, Enum):
    STANDARD = "standard"
    VIP = "vip"
    COUPLE = "couple"
    SWEETBOX = "sweetbox"


class Cinemas(SQLModel, table=True):
    __tablename__ = "cinemas"  # type: ignore[assigment]
    __table_args__ = (
        Index("idx_cinemas_city", "city"),
        Index("idx_cinemas_is_active", "is_active")
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    address: str = Field(sa_type=Text, nullable=False)
    city: str = Field(max_length=100, nullable=False)
    district: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, sa_type=Text)
    image_url: str | None = Field(default=None, max_length=500)
    latitude: Decimal = Field(
        sa_column=Column(
            Numeric(10, 8),
            default=None
        )
    )
    longitude: Decimal = Field(
        sa_column=Column(
            Numeric(11, 8),
            default=None
        )
    )
    is_active: bool = Field(default=True, nullable=False)
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
            server_default=text("TIMEZONE('utc',CURRENT_TIMESTAMP)"),
            onupdate=lambda: datetime.now(timezone.utc)
        )
    )

    # relationships
    rooms: list["Rooms"] = Relationship(
        back_populates="cinema"
    )


class Rooms(SQLModel, table=True):
    __tablename__ = "rooms"  # type: ignore[assigment]
    __table_args__ = (
        # check constraint
        CheckConstraint("total_rows > 0", name="ck_rooms_total_rows_positive"),
        CheckConstraint("seats_per_row > 0",
                        name="ck_rooms_seats_per_row_positive"),
        CheckConstraint("total_seats > 0",
                        name="ck_rooms_total_seats_positive"),


        # unique constraint
        UniqueConstraint("cinema_id", "name", name="uq_rooms_cinema_id_name"),


        # index constraint
        Index("idx_rooms_cinema_id", "cinema_id"),
        Index("idx_rooms_is_active", "is_active")

    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cinema_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("cinemas.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    name: str = Field(max_length=100, nullable=False)
    room_type: str = Field(default="2D", max_length=50, nullable=False)
    total_rows: int = Field(nullable=False, gt=0)
    seats_per_row: int = Field(nullable=False, gt=0)
    total_seats: int = Field(nullable=False, gt=0)
    is_active: bool = Field(nullable=False, default=True)
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

    # relationship
    cinema: "Cinemas" = Relationship(
        back_populates="rooms"
    )
    showtimes: list["Showtimes"] = Relationship(
        back_populates="room"
    )
    seats: list["Seats"] = Relationship(
        back_populates="room"
    )


class Seats(SQLModel, table=True):
    __tablename__ = "seats"  # type: ignore[assigment]
    __table_args__ = (
        # check constraint
        CheckConstraint("seat_number > 0",
                        name="ck_seats_seat_number_positive"),


        # unique constraint
        UniqueConstraint(
            "room_id",
            "row_label",
            "seat_number",
            name="uq_seats_room_id_row_label_seat_number"
        ),


        # index constraint
        Index("idx_seats_room_id", "room_id"),
        Index("idx_seats_seat_type", "seat_type")

    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    room_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("rooms.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    row_label: str = Field(
        sa_column=Column(
            CHAR(1),
            nullable=False
        )
    )
    seat_number: int = Field(nullable=False, gt=0)
    seat_type: SeatType = Field(
        sa_column=Column(
            SAEnum(
                SeatType,
                name="seat_type",
                create_type=False,
                native_enum=True,
                values_callable=lambda x: [e.value for e in x]
            ),
            nullable=False,
            default=SeatType.STANDARD
        )
    )
    price_multiplier: Decimal = Field(
        sa_column=Column(
            Numeric(3, 2),
            nullable=False,
            default=1.00  # 1.0 = standard, 1.5 = VIP
        )
    )
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('utc',CURRENT_TIMESTAMP)")
        )
    )

    # relationships
    room: "Rooms" = Relationship(
        back_populates="seats"
    )
    bookings: list["Bookings"] = Relationship(
        back_populates="seats",
        sa_relationship_kwargs={"secondary": "booking_seats"}
    )
