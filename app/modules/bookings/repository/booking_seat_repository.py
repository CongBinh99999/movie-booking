from uuid import UUID
from decimal import Decimal
from typing import Annotated
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.shared.dependencies import DbSession
from app.modules.bookings.models import Bookings, BookingSeats, BookingStatus


class BookingSeatRepository:
    """Data access layer cho BookingSeat entity (bảng liên kết booking-seat)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(
        self,
        booking_id: UUID,
        seats: list[dict],
    ) -> list[BookingSeats]:
        """Tạo nhiều booking_seat records cùng lúc.

        Args:
            booking_id: ID của booking.
            seats: Danh sách dict chứa seat_id và price.
                   Format: [{"seat_id": UUID, "price": Decimal}, ...]

        Returns:
            Danh sách BookingSeats vừa tạo.
        """
        now = datetime.now(timezone.utc)
        booking_seats: list[BookingSeats] = []

        for seat_data in seats:
            booking_seat = BookingSeats(
                booking_id=booking_id,
                seat_id=seat_data["seat_id"],
                price=seat_data["price"],
                created_at=now,
            )
            self.db.add(booking_seat)
            booking_seats.append(booking_seat)

        await self.db.flush()
        return booking_seats

    async def get_by_booking(self, booking_id: UUID) -> list[BookingSeats]:
        """Lấy tất cả booking_seat records theo booking_id.

        Args:
            booking_id: ID của booking.

        Returns:
            Danh sách BookingSeats thuộc booking.
        """
        result = await self.db.execute(
            select(BookingSeats)
            .where(BookingSeats.booking_id == booking_id)
        )
        return list(result.scalars().all())

    async def delete_by_booking(self, booking_id: UUID) -> int:
        """Xóa tất cả booking_seat records theo booking_id.

        Args:
            booking_id: ID của booking.

        Returns:
            Số lượng records đã xóa.
        """
        seats = await self.get_by_booking(booking_id)
        count = len(seats)

        for seat in seats:
            await self.db.delete(seat)

        await self.db.flush()
        return count

    async def get_booked_seats_for_showtime(
        self,
        showtime_id: UUID,
    ) -> list[UUID]:
        """Lấy danh sách seat_id đã được đặt cho một suất chiếu.

        Chỉ lấy từ các booking có trạng thái PENDING hoặc CONFIRMED
        (bỏ qua CANCELLED và EXPIRED).

        Args:
            showtime_id: ID của suất chiếu.

        Returns:
            Danh sách seat_id đã được đặt.
        """
        result = await self.db.execute(
            select(BookingSeats.seat_id)
            .join(Bookings, BookingSeats.booking_id == Bookings.id)
            .where(Bookings.showtime_id == showtime_id)
            .where(
                Bookings.status != BookingStatus.CANCELLED
            )
            .where(
                Bookings.status != BookingStatus.EXPIRED
            )
        )
        return list(result.scalars().all())

    async def count_by_booking(self, booking_id: UUID) -> int:
        """Đếm số ghế trong một booking.

        Args:
            booking_id: ID của booking.

        Returns:
            Số lượng ghế.
        """
        result = await self.db.execute(
            select(func.count(BookingSeats.id))
            .where(BookingSeats.booking_id == booking_id)
        )
        return result.scalar_one()

    async def count_booked_seats_for_showtime(
        self,
        showtime_id: UUID,
    ) -> int:
        """Đếm tổng số ghế đã đặt cho một suất chiếu.

        Chỉ tính từ booking PENDING hoặc CONFIRMED.

        Args:
            showtime_id: ID của suất chiếu.

        Returns:
            Tổng số ghế đã đặt.
        """
        result = await self.db.execute(
            select(func.count(BookingSeats.id))
            .join(Bookings, BookingSeats.booking_id == Bookings.id)
            .where(Bookings.showtime_id == showtime_id)
            .where(
                Bookings.status != BookingStatus.CANCELLED
            )
            .where(
                Bookings.status != BookingStatus.EXPIRED
            )
        )
        return result.scalar_one()

    async def is_seat_booked_for_showtime(
        self,
        showtime_id: UUID,
        seat_id: UUID,
    ) -> bool:
        """Kiểm tra xem ghế đã được đặt cho suất chiếu chưa.

        Chỉ booking PENDING hoặc CONFIRMED mới tính là đã đặt.

        Args:
            showtime_id: ID suất chiếu.
            seat_id: ID ghế cần kiểm tra.

        Returns:
            True nếu ghế đã được đặt.
        """
        result = await self.db.execute(
            select(func.count(BookingSeats.id))
            .join(Bookings, BookingSeats.booking_id == Bookings.id)
            .where(Bookings.showtime_id == showtime_id)
            .where(BookingSeats.seat_id == seat_id)
            .where(
                Bookings.status != BookingStatus.CANCELLED
            )
            .where(
                Bookings.status != BookingStatus.EXPIRED
            )
        )
        count = result.scalar_one()
        return count > 0


def get_booking_seat_repository(
    db: DbSession,
) -> BookingSeatRepository:
    return BookingSeatRepository(db)


BookingSeatRepoDeps = Annotated[
    BookingSeatRepository, Depends(get_booking_seat_repository)
]
