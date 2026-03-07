"""Booking service - business logic cho Booking entity."""
from decimal import Decimal
from uuid import UUID
from datetime import datetime, timezone

import redis.asyncio as aioredis

from app.core.config import get_setting
from app.modules.bookings.models import BookingStatus
from app.modules.bookings.repository.booking_repository import BookingRepository
from app.modules.bookings.repository.booking_seat_repository import BookingSeatRepository
from app.modules.bookings.schemas.domain import (
    BookingCreate,
    BookingDTO,
    BookingCalculation,
    SeatWithPrice,
    SeatAvailabilityInfo,
    SeatStatus,
)
from app.modules.bookings.exceptions import (
    BookingNotFoundError,
    BookingExpiredError,
    BookingAlreadyConfirmedError,
    BookingAlreadyCancelledError,
    BookingNotPendingError,
    BookingOwnershipError,
    SeatAlreadyBookedError,
    SeatLockedError,
    SeatsNotAvailableError,
    InvalidSeatSelectionError,
)
from app.modules.showtimes.repository import ShowtimeRepository
from app.modules.showtimes.exceptions import ShowtimeNotFoundError
from app.modules.cinemas.repository.seat_repository import SeatRepository


class BookingService:
    """Service xử lý business logic cho Booking."""

    LOCK_KEY_PREFIX = "lock:showtime"

    def __init__(
        self,
        booking_repo: BookingRepository,
        booking_seat_repo: BookingSeatRepository,
        showtime_repo: ShowtimeRepository,
        seat_repo: SeatRepository,
        redis: aioredis.Redis,
    ):
        self.booking_repo = booking_repo
        self.booking_seat_repo = booking_seat_repo
        self.showtime_repo = showtime_repo
        self.seat_repo = seat_repo
        self.redis = redis

    def _lock_key(self, showtime_id: UUID, seat_id: UUID) -> str:
        """Tạo Redis key cho seat lock."""
        return f"{self.LOCK_KEY_PREFIX}:{showtime_id}:seat:{seat_id}"

    async def acquire_seat_locks(
        self,
        showtime_id: UUID,
        seat_ids: list[UUID],
        user_id: UUID,
        ttl: int | None = None,
    ) -> bool:
        """Khóa ghế tạm thời bằng Redis SETNX. Rollback nếu bất kỳ ghế nào đã bị khóa."""
        if ttl is None:
            ttl = get_setting().SEAT_LOCK_TTL

        user_id_str = str(user_id)
        keys = [self._lock_key(showtime_id, sid) for sid in seat_ids]
        acquired_keys: list[str] = []

        try:
            for i, key in enumerate(keys):
                was_set = await self.redis.set(
                    key, user_id_str, nx=True, ex=ttl
                )

                if was_set:
                    acquired_keys.append(key)
                else:
                    locked_by = await self.redis.get(key)
                    if locked_by == user_id_str:
                        await self.redis.expire(key, ttl)
                        acquired_keys.append(key)
                    else:
                        locked_by_uuid = (
                            UUID(locked_by) if locked_by else None
                        )

                        if acquired_keys:
                            await self.redis.delete(*acquired_keys)

                        raise SeatLockedError(
                            seat_id=seat_ids[i],
                            showtime_id=showtime_id,
                            locked_by=locked_by_uuid,
                        )
            return True

        except SeatLockedError:
            raise
        except Exception:
            if acquired_keys:
                await self.redis.delete(*acquired_keys)
            raise

    async def release_seat_locks(
        self,
        showtime_id: UUID,
        seat_ids: list[UUID],
    ) -> None:
        """Giải phóng lock ghế trên Redis."""
        if not seat_ids:
            return

        keys = [self._lock_key(showtime_id, sid) for sid in seat_ids]
        deleted_count = await self.redis.delete(*keys)

    async def get_locked_seats(self, showtime_id: UUID) -> list[UUID]:
        """Lấy danh sách seat_id đang bị khóa (Redis SCAN)."""
        pattern = f"{self.LOCK_KEY_PREFIX}:{showtime_id}:seat:*"
        locked_seat_ids: list[UUID] = []

        async for key in self.redis.scan_iter(match=pattern, count=100):
            key_str = key if isinstance(key, str) else key.decode("utf-8")
            seat_id_str = key_str.rsplit(":", maxsplit=1)[-1]
            try:
                locked_seat_ids.append(UUID(seat_id_str))
            except ValueError:
                pass

        return locked_seat_ids

    async def is_seat_locked(
        self, showtime_id: UUID, seat_id: UUID
    ) -> tuple[bool, UUID | None]:
        """Kiểm tra ghế có đang bị khóa không."""
        key = self._lock_key(showtime_id, seat_id)
        locked_by = await self.redis.get(key)

        if locked_by is None:
            return False, None

        try:
            return True, UUID(locked_by)
        except ValueError:
            return True, None

    async def create_booking(
        self, user_id: UUID, showtime_id: UUID, seat_ids: list[UUID]
    ) -> BookingDTO:
        """Tạo booking mới."""

        showtime = await self.showtime_repo.get_by_id(showtime_id)
        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        now = datetime.now(timezone.utc)
        start_time = showtime.start_time
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        if start_time <= now:
            raise ShowtimeNotFoundError(showtime_id)

        seats = await self.seat_repo.get_by_ids(seat_ids)
        if len(seats) != len(seat_ids):
            found_ids = {s.id for s in seats}
            missing_ids = [sid for sid in seat_ids if sid not in found_ids]
            raise InvalidSeatSelectionError(
                seat_ids=missing_ids,
                room_id=showtime.room_id,
                reason="Một hoặc nhiều ghế không tồn tại",
            )

        invalid_seats = [s for s in seats if s.room_id != showtime.room_id]
        if invalid_seats:
            raise InvalidSeatSelectionError(
                seat_ids=[s.id for s in invalid_seats],
                room_id=showtime.room_id,
                reason="Ghế không thuộc phòng chiếu của suất chiếu này",
            )

        inactive_seats = [s for s in seats if not s.is_active]
        if inactive_seats:
            raise SeatsNotAvailableError(
                seat_ids=[s.id for s in inactive_seats],
                showtime_id=showtime_id,
            )

        booked_seat_ids = await self.booking_seat_repo.get_booked_seats_for_showtime(
            showtime_id
        )
        already_booked = [sid for sid in seat_ids if sid in booked_seat_ids]
        if already_booked:
            raise SeatAlreadyBookedError(
                seat_id=already_booked[0],
                showtime_id=showtime_id,
            )

        await self.acquire_seat_locks(showtime_id, seat_ids, user_id)

        calculation = self._calculate_prices(showtime, seats)

        booking_data = BookingCreate(
            user_id=user_id,
            showtime_id=showtime_id,
            seat_ids=seat_ids,
        )

        booking = await self.booking_repo.create(
            booking_data=booking_data,
            total_amount=calculation.total_amount,
            seat_prices={
                sp.id: sp.final_price for sp in calculation.seats
            },
        )

        return BookingDTO.model_validate(booking)

    async def confirm_booking(
        self, booking_id: UUID, user_id: UUID
    ) -> BookingDTO:
        """Xác nhận booking (PENDING → CONFIRMED)."""
        booking = await self._get_and_verify_ownership(booking_id, user_id)

        if booking.status == BookingStatus.CONFIRMED:
            raise BookingAlreadyConfirmedError(booking_id)

        if booking.status != BookingStatus.PENDING:
            raise BookingNotPendingError(booking_id, booking.status.value)

        now = datetime.now(timezone.utc)
        if booking.expires_at < now:
            raise BookingExpiredError(booking_id, booking.expires_at)

        confirmed = await self.booking_repo.confirm_booking(booking_id)
        if confirmed is None:
            raise BookingNotFoundError(booking_id=booking_id)

        booking_seats = await self.booking_seat_repo.get_by_booking(booking_id)
        seat_ids = [bs.seat_id for bs in booking_seats]
        await self.release_seat_locks(booking.showtime_id, seat_ids)

        return BookingDTO.model_validate(confirmed)

    async def cancel_booking(
        self,
        booking_id: UUID,
        user_id: UUID,
        reason: str | None = None,
    ) -> BookingDTO:
        """Hủy booking."""
        booking = await self._get_and_verify_ownership(booking_id, user_id)

        if booking.status == BookingStatus.CANCELLED:
            raise BookingAlreadyCancelledError(booking_id)

        if booking.status not in (
            BookingStatus.PENDING, BookingStatus.CONFIRMED,
        ):
            raise BookingNotPendingError(booking_id, booking.status.value)

        cancelled = await self.booking_repo.cancel_booking(
            booking_id, reason
        )
        if cancelled is None:
            raise BookingNotFoundError(booking_id=booking_id)

        booking_seats = await self.booking_seat_repo.get_by_booking(booking_id)
        seat_ids = [bs.seat_id for bs in booking_seats]
        await self.release_seat_locks(booking.showtime_id, seat_ids)

        return BookingDTO.model_validate(cancelled)

    async def expire_pending_bookings(self) -> int:
        """Hết hạn các booking PENDING đã quá expires_at."""
        now = datetime.now(timezone.utc)
        expired_bookings = await self.booking_repo.get_expired_pending_bookings(
            before=now
        )

        if not expired_bookings:
            return 0

        count = 0
        for booking in expired_bookings:
            result = await self.booking_repo.expire_booking(booking.id)
            if result is not None:

                booking_seats = await self.booking_seat_repo.get_by_booking(
                    booking.id
                )
                seat_ids = [bs.seat_id for bs in booking_seats]
                await self.release_seat_locks(booking.showtime_id, seat_ids)
                count += 1

        return count

    async def get_booking_by_id(
        self,
        booking_id: UUID,
        user_id: UUID | None = None,
    ) -> BookingDTO:
        """Lấy booking theo ID."""
        if user_id is not None:
            booking = await self._get_and_verify_ownership(
                booking_id, user_id
            )
        else:
            booking = await self.booking_repo.get_by_id(booking_id)
            if booking is None:
                raise BookingNotFoundError(booking_id=booking_id)

        return BookingDTO.model_validate(booking)

    async def get_booking_by_code(
        self,
        booking_code: str,
        user_id: UUID | None = None,
    ) -> BookingDTO:
        """Lấy booking theo mã booking."""
        booking = await self.booking_repo.get_by_booking_code(booking_code)
        if booking is None:
            raise BookingNotFoundError(booking_code=booking_code)

        if user_id is not None and booking.user_id != user_id:
            raise BookingOwnershipError(booking.id, user_id)

        return BookingDTO.model_validate(booking)

    async def get_user_bookings(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[BookingDTO], int]:
        """Lấy danh sách booking của user có phân trang."""
        bookings = await self.booking_repo.get_by_user(
            user_id, skip=skip, limit=limit
        )
        total = await self.booking_repo.count_by_user(user_id)

        items = [BookingDTO.model_validate(b) for b in bookings]
        return items, total

    async def get_available_seats(
        self, showtime_id: UUID
    ) -> list[SeatAvailabilityInfo]:
        """Lấy danh sách ghế kèm trạng thái cho suất chiếu."""
        showtime = await self.showtime_repo.get_by_id(showtime_id)
        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        all_seats = await self.seat_repo.get_by_room_type(
            room_id=showtime.room_id
        )
        active_seats = [s for s in all_seats if s.is_active]

        booked_seat_ids = set(
            await self.booking_seat_repo.get_booked_seats_for_showtime(
                showtime_id
            )
        )

        locked_seat_ids = set(await self.get_locked_seats(showtime_id))

        base_price = showtime.base_price
        result: list[SeatAvailabilityInfo] = []

        for seat in active_seats:
            final_price = base_price * seat.price_multiplier

            if seat.id in booked_seat_ids:
                status = SeatStatus.BOOKED
            elif seat.id in locked_seat_ids:
                status = SeatStatus.LOCKED
            else:
                status = SeatStatus.AVAILABLE

            result.append(
                SeatAvailabilityInfo(
                    id=seat.id,
                    row_label=seat.row_label,
                    seat_number=seat.seat_number,
                    seat_type=seat.seat_type,
                    base_price=base_price,
                    price_multiplier=seat.price_multiplier,
                    final_price=final_price,
                    status=status,
                )
            )

        return result

    async def calculate_booking_total(
        self, showtime_id: UUID, seat_ids: list[UUID]
    ) -> BookingCalculation:
        """Tính giá booking."""
        showtime = await self.showtime_repo.get_by_id(showtime_id)
        if showtime is None:
            raise ShowtimeNotFoundError(showtime_id)

        seats = await self.seat_repo.get_by_ids(seat_ids)
        if len(seats) != len(seat_ids):
            found_ids = {s.id for s in seats}
            missing_ids = [sid for sid in seat_ids if sid not in found_ids]
            raise InvalidSeatSelectionError(
                seat_ids=missing_ids,
                room_id=showtime.room_id,
                reason="Một hoặc nhiều ghế không tồn tại",
            )

        invalid_seats = [s for s in seats if s.room_id != showtime.room_id]
        if invalid_seats:
            raise InvalidSeatSelectionError(
                seat_ids=[s.id for s in invalid_seats],
                room_id=showtime.room_id,
            )

        return self._calculate_prices(showtime, seats)

    @staticmethod
    def _calculate_prices(showtime, seats) -> BookingCalculation:
        """Tính giá cho danh sách ghế."""
        base_price = showtime.base_price
        seat_prices: list[SeatWithPrice] = []
        total = Decimal("0")

        for seat in seats:
            final_price = base_price * seat.price_multiplier
            total += final_price

            seat_prices.append(
                SeatWithPrice(
                    id=seat.id,
                    row_label=seat.row_label,
                    seat_number=seat.seat_number,
                    seat_type=seat.seat_type,
                    base_price=base_price,
                    price_multiplier=seat.price_multiplier,
                    final_price=final_price,
                )
            )

        return BookingCalculation(
            seats=seat_prices,
            total_amount=total,
        )

    async def _get_and_verify_ownership(
        self, booking_id: UUID, user_id: UUID
    ):
        """Lấy booking và verify ownership."""
        booking = await self.booking_repo.get_by_id(booking_id)
        if booking is None:
            raise BookingNotFoundError(booking_id=booking_id)

        if booking.user_id != user_id:
            raise BookingOwnershipError(booking_id, user_id)

        return booking
