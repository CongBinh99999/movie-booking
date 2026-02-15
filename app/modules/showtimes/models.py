from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text, Index, CheckConstraint, Column, ForeignKey, Numeric
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from decimal import Decimal

if TYPE_CHECKING:
    from app.modules.bookings.models import Bookings
    from app.modules.movies.models import Movies
    from app.modules.cinemas.models import Rooms


class Showtimes(SQLModel, table=True):
    __tablename__ = "showtimes"  # type: ignore[assigment]
    __table_args__ = (
        # check constraint
        CheckConstraint("base_price > 0",
                        name="ck_showtimes_base_price_positive"),
        CheckConstraint("end_time > start_time", name="valid_time_range"),


        # index constraint
        Index("idx_showtimes_movie_id", "movie_id"),
        Index("idx_showtimes_room_id", "room_id"),
        Index("idx_showtimes_start_time", "start_time"),
        Index("idx_showtimes_is_active", "is_active"),
        Index("idx_showtimes_room_time", "room_id", "start_time", "end_time")
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    movie_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("movies.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    room_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("rooms.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    start_time: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False
        )
    )
    end_time: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False
        )
    )
    base_price: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False
        )
    )
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('utc',CURRENT_TIMESTAMP)")
        )
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('utc',CURRENT_TIMESTAMP)"),
            onupdate=lambda: datetime.now(timezone.utc)
        )
    )

    # relationships
    bookings: list["Bookings"] = Relationship(
        back_populates="showtime"
    )
    movie: "Movies" = Relationship(
        back_populates="showtimes"
    )
    room: "Rooms" = Relationship(
        back_populates="showtimes"
    )
