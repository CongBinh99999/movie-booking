from decimal import Decimal
from uuid import uuid4, UUID
from typing import Annotated
from datetime import datetime, timezone, timedelta
import time
import random

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
import sqlalchemy.orm

from app.shared.dependencies import DbSession
from app.modules.bookings.models import Bookings, BookingSeats, BookingStatus
from app.modules.bookings.schemas.domain import BookingCreate, BookingUpdate
from app.core.config import get_setting


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 20) -> list[Bookings]:
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_booking_code(self, code: str) -> Bookings | None:
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.booking_code == code)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        booking_data: BookingCreate,
        total_amount: Decimal,
        seat_prices: dict[UUID, Decimal]
    ) -> Bookings:
        settings = get_setting()

        booking_code = await self._generate_booking_code()

        expires_at = datetime.now(timezone.utc) + \
            timedelta(seconds=settings.SEAT_LOCK_TTL)

        now = datetime.now(timezone.utc)
        booking = Bookings(
            user_id=booking_data.user_id,
            showtime_id=booking_data.showtime_id,
            booking_code=booking_code,
            status=BookingStatus.PENDING,
            total_amount=total_amount,
            expires_at=expires_at,
            confirmed_at=None,
            cancelled_at=None,
            cancellation_reason=None,
            created_at=now,
            updated_at=now
        )

        self.db.add(booking)
        await self.db.flush()

        now = datetime.now(timezone.utc)
        for seat_id in booking_data.seat_ids:
            seat_price = seat_prices.get(seat_id, Decimal("0"))
            booking_seat = BookingSeats(
                booking_id=booking.id,
                seat_id=seat_id,
                price=seat_price,
                created_at=now
            )
            self.db.add(booking_seat)

        await self.db.flush()
        await self.db.refresh(booking)

        return booking

    async def _generate_booking_code(self) -> str:
        """Tạo mã booking duy nhất.

        Format: BK + 10 ký tự timestamp + 6 ký tự UUID = 18 chars (max_length=20).
        Retry tối đa 3 lần nếu bị trùng.
        """
        max_retries = 3
        for attempt in range(max_retries):
            timestamp = str(int(time.time() * 1000000))[-10:]
            uuid_part = str(uuid4()).replace('-', '')[:6]

            if attempt > 0:
                # Thêm random suffix khi retry (vẫn <= 20 chars)
                code = f"BK{timestamp}{uuid_part}{random.randint(0, 9)}"
            else:
                code = f"BK{timestamp}{uuid_part}"

            # Verify uniqueness
            result = await self.db.execute(
                select(Bookings.booking_code).where(
                    Bookings.booking_code == code)
            )
            if result.scalar_one_or_none() is None:
                return code

        # Fallback: dùng UUID-based code nếu tất cả retry thất bại (18 chars)
        return f"BK{uuid4().hex[:16].upper()}"

    async def get_by_id(self, booking_id: UUID) -> Bookings | None:
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.id == booking_id)
        )

        return result.scalar_one_or_none()

    async def update(self, booking: Bookings, data: BookingUpdate) -> Bookings:
        updated_data = data.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(booking, key, value)

        booking.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(booking)

        return booking

    async def delete(self, booking: Bookings) -> None:
        await self.db.delete(booking)
        await self.db.flush()

    async def get_by_showtime(self, showtime_id: UUID, skip: int = 0, limit: int = 100) -> list[Bookings]:
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.showtime_id == showtime_id)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_status(self, status: BookingStatus, skip: int = 0, limit: int = 100) -> list[Bookings]:
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.status == status)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def count_by_user(self, user_id: UUID) -> int:
        count = await self.db.execute(
            select(func.count(Bookings.id)).select_from(Bookings)
            .where(Bookings.user_id == user_id)
        )

        return count.scalar_one()

    async def count_by_showtime(self, showtime_id: UUID) -> int:
        count = await self.db.execute(
            select(func.count(Bookings.id)).select_from(Bookings)
            .where(Bookings.showtime_id == showtime_id)
        )

        return count.scalar_one()

    async def update_status(self, booking_id: UUID, status: BookingStatus) -> Bookings | None:
        """Cập nhật trạng thái của booking"""
        booking = await self.get_by_id(booking_id)
        if not booking:
            return None

        booking.status = status
        booking.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(booking)
        return booking

    async def confirm_booking(self, booking_id: UUID) -> Bookings | None:
        """Xác nhận booking - chuyển trạng thái từ PENDING sang CONFIRMED"""
        booking = await self.get_by_id(booking_id)
        if not booking:
            return None

        now = datetime.now(timezone.utc)
        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = now
        booking.updated_at = now

        await self.db.flush()
        await self.db.refresh(booking)
        return booking

    async def cancel_booking(self, booking_id: UUID, reason: str | None = None) -> Bookings | None:
        """Hủy booking - chuyển trạng thái sang CANCELLED"""
        booking = await self.get_by_id(booking_id)
        if not booking:
            return None

        now = datetime.now(timezone.utc)
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = now
        booking.cancellation_reason = reason
        booking.updated_at = now

        await self.db.flush()
        await self.db.refresh(booking)
        return booking

    async def expire_booking(self, booking_id: UUID) -> Bookings | None:
        """Hết hạn booking - chuyển trạng thái sang EXPIRED"""
        booking = await self.get_by_id(booking_id)
        if not booking:
            return None

        now = datetime.now(timezone.utc)
        booking.status = BookingStatus.EXPIRED
        booking.updated_at = now

        await self.db.flush()
        await self.db.refresh(booking)
        return booking

    async def get_expired_pending_bookings(self, before: datetime) -> list[Bookings]:
        """Lấy danh sách các booking PENDING đã hết hạn trước thời điểm specified"""
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.status == BookingStatus.PENDING)
            .where(Bookings.expires_at < before)
        )
        return list(result.scalars().all())

    async def exists_by_booking_code(self, code: str) -> bool:
        """Kiểm tra xem booking code đã tồn tại chưa"""
        result = await self.db.execute(
            select(func.count(Bookings.id))
            .where(Bookings.booking_code == code)
        )
        count = result.scalar_one()
        return count > 0

    async def is_seat_booked_for_showtime(self, showtime_id: UUID, seat_id: UUID) -> bool:
        """Kiểm tra xem ghế đã được đặt cho suất chiếu chưa

        Chỉ các booking không ở trạng thái CANCELLED hoặc EXPIRED mới được tính là đã đặt
        """
        result = await self.db.execute(
            select(func.count(BookingSeats.id))
            .join(Bookings, BookingSeats.booking_id == Bookings.id)
            .where(Bookings.showtime_id == showtime_id)
            .where(BookingSeats.seat_id == seat_id)
            .where(Bookings.status != BookingStatus.CANCELLED)
            .where(Bookings.status != BookingStatus.EXPIRED)
        )
        count = result.scalar_one()
        return count > 0

    async def get_by_id_with_seats(self, booking_id: UUID) -> Bookings | None:
        """Lấy booking kèm thông tin chi tiết về ghế đã đặt"""
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.id == booking_id)
            .options(
                sqlalchemy.orm.joinedload(Bookings.seats)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_payments(self, booking_id: UUID) -> Bookings | None:
        """Lấy booking kèm thông tin chi tiết về thanh toán"""
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.id == booking_id)
            .options(
                sqlalchemy.orm.joinedload(Bookings.payments)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_full(self, booking_id: UUID) -> Bookings | None:
        """Lấy đầy đủ thông tin booking bao gồm ghế và thanh toán"""
        result = await self.db.execute(
            select(Bookings)
            .where(Bookings.id == booking_id)
            .options(
                sqlalchemy.orm.joinedload(Bookings.seats),
                sqlalchemy.orm.joinedload(Bookings.payments)
            )
        )
        return result.scalar_one_or_none()


def get_booking_repository(
    db: DbSession
) -> BookingRepository:
    return BookingRepository(db)


BookingRepoDeps = Annotated[BookingRepository, Depends(get_booking_repository)]
