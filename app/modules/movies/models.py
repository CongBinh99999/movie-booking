from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.types import DateTime, Date
from sqlalchemy import text, Column, Text, CheckConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY

from uuid import uuid4, UUID
from typing import TYPE_CHECKING
from datetime import datetime, timezone, date


if TYPE_CHECKING:
    from app.modules.showtimes.models import Showtimes


class MovieGenres(SQLModel, table=True):
    __tablename__ = "movie_genres"  # type: ignore [assigment]
    __table_args__ = (
        Index("idx_movie_genres_movie_id", "movie_id"),
        Index("idx_movie_genres_genre_id", "genre_id")
    )

    movie_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("movies.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True
        )
    )
    genre_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("genres.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True
        )

    )


class Genres(SQLModel, table=True):
    __tablename__ = "genres"  # type:ignore [assigment]

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=100, nullable=False, unique=True)
    slug: str = Field(max_length=100, nullable=False, unique=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)")
        )
    )

    # relationships
    movies: list["Movies"] = Relationship(
        back_populates="genres",
        link_model=MovieGenres
    )


class Movies(SQLModel, table=True):
    __tablename__ = "movies"  # type:ignore [asssigment]
    __table_args__ = (
        # check constaint
        CheckConstraint(
            "duration_minutes > 0 AND duration_minutes <= 500",
            name="ck_movies_duration_minutes_range"
        ),


        # index constraint
        Index("idx_movies_title", "title"),
        Index("idx_movies_release_date", "release_date"),
        Index("idx_movies_is_active", "is_active")

    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    original_title: str = Field(max_length=255)
    description: str | None = Field(default=None, sa_type=Text)
    duration_minutes: int = Field(nullable=False, gt=0, le=500)
    release_date: date | None = Field(sa_column=Column(Date, default=None))
    end_date: date | None = Field(sa_column=Column(Date, default=None))
    poster_url: str | None = Field(default=None, max_length=500)
    trailer_url: str | None = Field(default=None, max_length=500)
    director: str | None = Field(default=None, max_length=255)
    cast_members: list[str] = Field(
        default_factory=list,
        sa_column=Column(
            ARRAY(Text),
            nullable=False,
            server_default="{}"
        )
    )
    language: str | None = Field(default=None, max_length=50)
    subtitle: str | None = Field(default=None, max_length=50)
    age_rating: str | None = Field(default=None, max_length=10)
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

    # relationships
    genres: list["Genres"] = Relationship(
        back_populates="movies",
        link_model=MovieGenres
    )
    showtimes: list["Showtimes"] = Relationship(
        back_populates="movie"
    )
