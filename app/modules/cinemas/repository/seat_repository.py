from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import DbSession
from typing import Annotated, cast
from fastapi import Depends
from app.modules.cinemas.models import Seats, SeatType
from uuid import UUID
from app.modules.cinemas.schemas.domain import SeatCreate, SeatUpdate
from decimal import Decimal
from sqlalchemy import select, delete, and_, func, update, exists
from sqlmodel import col
from sqlalchemy.engine import CursorResult


class SeatRepository:
    """Repository xử lý các thao tác CRUD cho entity Seat (ghế ngồi)."""

    def __init__(self, db: AsyncSession):
        """Khởi tạo repository với database session.

        Args:
            db: AsyncSession kết nối với database.
        """
        self.db = db

    async def get_by_id(self, seat_id: UUID) -> Seats | None:
        """Lấy ghế theo ID.

        Args:
            seat_id: UUID của ghế cần tìm.

        Returns:
            Seats nếu tìm thấy, None nếu không tồn tại.
        """
        result = await self.db.execute(
            select(Seats).where(Seats.id == seat_id)
        )
        return result.scalar_one_or_none()

    async def get_by_ids(self, seat_ids: list[UUID]) -> list[Seats]:
        """Lấy nhiều ghế theo danh sách ID.

        Args:
            seat_ids: Danh sách UUID của các ghế.

        Returns:
            Danh sách ghế tìm thấy (có thể ít hơn số ID truyền vào).
        """
        result = await self.db.execute(
            select(Seats).where(col(Seats.id).in_(seat_ids))
        )
        return list(result.scalars().all())

    async def get_by_room_type(self, room_id: UUID, seat_type: SeatType | None = None) -> list[Seats]:
        """Lấy tất cả ghế trong một phòng.

        Args:
            room_id: UUID của phòng.
            seat_type: Loại ghế (STANDARD, VIP, COUPLE, SWEETBOX).

        Returns:
            Danh sách ghế, sắp xếp theo hàng (row_label) và số ghế (seat_number).
        """
        query = (
            select(Seats)
            .where(Seats.room_id == room_id)
        )
        if seat_type: 
            query = query.where(and_(Seats.seat_type == seat_type))
        
        query = query.order_by(Seats.row_label, Seats.seat_number)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_row(self, room_id: UUID, row_label: str) -> list[Seats]:
        """Lấy tất cả ghế trong một hàng.

        Args:
            room_id: UUID của phòng.
            row_label: Ký tự hàng (A, B, C...).

        Returns:
            Danh sách ghế trong hàng, sắp xếp theo số ghế.
        """
        result = await self.db.execute(
            select(Seats)
            .where(
                and_(
                    Seats.room_id == room_id,
                    Seats.row_label == row_label
                )
            )
            .order_by(Seats.seat_number)
        )
        return list(result.scalars().all())

    async def create_many(self, room_id: UUID, seats: list[SeatCreate]) -> list[Seats]:
        """Tạo nhiều ghế cùng lúc (bulk insert).

        Args:
            room_id: UUID của phòng chứa các ghế.
            seats: Danh sách dữ liệu ghế cần tạo.

        Returns:
            Danh sách ghế vừa được tạo.
        """
        db_seats = [
            Seats(
                room_id=room_id,
                row_label=seat.row_label,
                seat_number=seat.seat_number,
                seat_type=seat.seat_type,
                price_multiplier=seat.price_multiplier
            )
            for seat in seats
        ]

        self.db.add_all(db_seats)
        await self.db.flush()

        return db_seats

    async def update(self, seat: Seats, data: SeatUpdate) -> Seats:
        """Cập nhật thông tin ghế.

        Chỉ cập nhật các field được truyền vào (exclude_unset=True).

        Args:
            seat: Entity ghế cần cập nhật.
            data: Dữ liệu cập nhật (partial update).

        Returns:
            Ghế sau khi cập nhật.
        """
        updated_data = data.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(seat, key, value)

        await self.db.flush()
        await self.db.refresh(seat)

        return seat

    async def bulk_update_type(
        self,
        seat_ids: list[UUID],
        seat_type: SeatType,
        price_multiplier: Decimal
    ) -> list[Seats]:
        """Cập nhật loại ghế và hệ số giá cho nhiều ghế (bulk update).

        Args:
            seat_ids: Danh sách UUID của các ghế cần cập nhật.
            seat_type: Loại ghế mới.
            price_multiplier: Hệ số giá mới.

        Returns:
            Danh sách ghế sau khi cập nhật.
        """
        result = await self.db.scalars(
            update(Seats)
            .where(col(Seats.id).in_(seat_ids))
            .values(
                seat_type=seat_type,
                price_multiplier=price_multiplier
            )
            .returning(Seats)
        )

        await self.db.flush()

        return list(result.all())

    async def _update_active_status(self, seat_id: UUID, status: bool) -> Seats | None:
        """Cập nhật trạng thái hoạt động của ghế (internal method).

        Args:
            seat_id: UUID của ghế.
            status: Trạng thái mới (True = active, False = inactive).

        Returns:
            Ghế sau khi cập nhật, None nếu không tìm thấy.
        """
        result = await self.db.execute(
            update(Seats)
            .where(Seats.id == seat_id)
            .values(is_active=status)
            .returning(Seats)
        )

        await self.db.flush()

        return result.scalar_one_or_none()

    async def activate(self, seat_id: UUID) -> Seats | None:
        """Kích hoạt ghế (set is_active = True).

        Args:
            seat_id: UUID của ghế.

        Returns:
            Ghế sau khi kích hoạt, None nếu không tìm thấy.
        """
        return await self._update_active_status(seat_id, True)

    async def deactivate(self, seat_id: UUID) -> Seats | None:
        """Vô hiệu hoá ghế (set is_active = False).

        Ghế bị vô hiệu hoá sẽ không thể đặt trong các suất chiếu mới.

        Args:
            seat_id: UUID của ghế.

        Returns:
            Ghế sau khi vô hiệu hoá, None nếu không tìm thấy.
        """
        return await self._update_active_status(seat_id, False)

    async def delete(self, seat_id: UUID) -> bool:
        """Xoá ghế theo ID (hard delete).

        Args:
            seat_id: UUID của ghế cần xoá.

        Returns:
            True nếu xoá thành công, False nếu không tìm thấy ghế.
        """
        result = await self.db.execute(
            delete(Seats).where(Seats.id == seat_id)
        )

        await self.db.flush()

        return cast(CursorResult, result).rowcount > 0

    async def delete_by_room(self, room_id: UUID) -> int:
        """Xoá tất cả ghế trong một phòng (bulk delete).

        Thường dùng khi cần reset lại sơ đồ ghế của phòng.

        Args:
            room_id: UUID của phòng.

        Returns:
            Số lượng ghế đã xoá.
        """
        result = await self.db.execute(
            delete(Seats).where(Seats.room_id == room_id)
        )

        await self.db.flush()

        return cast(CursorResult, result).rowcount or 0

    async def count_by_room(self, room_id: UUID) -> int:
        """Đếm số ghế trong một phòng.

        Args:
            room_id: UUID của phòng.

        Returns:
            Số lượng ghế.
        """
        result = await self.db.execute(
            select(func.count(Seats.id))
            .select_from(Seats)
            .where(Seats.room_id == room_id)
        )
        return result.scalar_one()

    async def count_by_room_and_type(self, room_id: UUID, seat_type: SeatType) -> int:
        """Đếm số ghế theo loại trong một phòng.

        Args:
            room_id: UUID của phòng.
            seat_type: Loại ghế cần đếm.

        Returns:
            Số lượng ghế theo loại.
        """
        result = await self.db.execute(
            select(func.count(Seats.id))
            .select_from(Seats)
            .where(
                and_(
                    Seats.room_id == room_id,
                    Seats.seat_type == seat_type
                )
            )
        )
        return result.scalar_one()

    async def exists_in_room(self, room_id: UUID, row_label: str, seat_number: int) -> bool:
        """Kiểm tra ghế đã tồn tại trong phòng theo vị trí.

        Args:
            room_id: UUID của phòng.
            row_label: Ký tự hàng (A, B, C...).
            seat_number: Số ghế trong hàng.

        Returns:
            True nếu ghế đã tồn tại, False nếu chưa.
        """
        result = await self.db.execute(
            select(
                exists().where(
                    and_(
                        Seats.room_id == room_id,
                        Seats.row_label == row_label,
                        Seats.seat_number == seat_number
                    )
                )
            )
        )
        return result.scalar_one()


def get_seat_repository(db: DbSession) -> SeatRepository:
    """Factory function để tạo SeatRepository (FastAPI dependency).

    Args:
        db: Database session từ dependency injection.

    Returns:
        Instance của SeatRepository.
    """
    return SeatRepository(db)


SeatRepoDep = Annotated[SeatRepository, Depends(get_seat_repository)]
