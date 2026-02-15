from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import DbSession
from typing import Annotated
from uuid import UUID
from app.modules.cinemas.models import Rooms
from app.modules.cinemas.schemas.domain import RoomCreate, RoomUpdate
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.orm import contains_eager, selectinload
from sqlmodel import col


class RoomRepository:
    """Repository xử lý các thao tác CRUD cho entity Room (phòng chiếu)."""

    def __init__(self, db: AsyncSession):
        """Khởi tạo repository với database session.

        Args:
            db: AsyncSession kết nối với database.
        """
        self.db = db

    async def get_by_id(self, room_id: UUID) -> Rooms | None:
        """Lấy phòng chiếu theo ID.

        Args:
            room_id: UUID của phòng cần tìm.

        Returns:
            Rooms nếu tìm thấy, None nếu không tồn tại.
        """
        result = await self.db.execute(
            select(Rooms)
            .where(Rooms.id == room_id)
        )

        return result.scalar_one_or_none()

    async def get_by_cinema(self, cinema_id: UUID, skip: int = 0, limit: int = 100) -> list[Rooms]:
        """Lấy danh sách phòng chiếu theo cinema với phân trang.

        Args:
            cinema_id: UUID của cinema.
            skip: Số lượng bản ghi bỏ qua (mặc định 0).
            limit: Số lượng bản ghi tối đa (mặc định 100).

        Returns:
            Danh sách phòng chiếu, sắp xếp theo tên.
        """
        result = await self.db.execute(
            select(Rooms)
            .where(Rooms.cinema_id == cinema_id)
            .order_by(Rooms.name)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def create(self, cinema_id: UUID, data: RoomCreate) -> Rooms:
        """Tạo mới một phòng chiếu.

        Tự động tính total_seats = total_rows * seats_per_row.

        Args:
            cinema_id: UUID của cinema chứa phòng.
            data: Dữ liệu phòng cần tạo.

        Returns:
            Phòng vừa được tạo với ID được generate.
        """
        room = Rooms(
            cinema_id=cinema_id,
            name=data.name,
            room_type=data.room_type,
            total_rows=data.total_rows,
            seats_per_row=data.seats_per_row,
            total_seats=data.total_rows * data.seats_per_row
        )

        self.db.add(room)
        await self.db.flush()
        await self.db.refresh(room)

        return room

    async def update(self, room: Rooms, data: RoomUpdate) -> Rooms:
        """Cập nhật thông tin phòng chiếu.

        Chỉ cập nhật các field được truyền vào (exclude_unset=True).

        Args:
            room: Entity phòng cần cập nhật.
            data: Dữ liệu cập nhật (partial update).

        Returns:
            Phòng sau khi cập nhật.
        """
        updated_data = data.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(room, key, value)

        await self.db.flush()
        await self.db.refresh(room)

        return room

    async def delete(self, room: Rooms) -> None:
        """Xoá phòng chiếu (hard delete).

        Lưu ý: Cascade delete sẽ xoá tất cả ghế trong phòng.

        Args:
            room: Entity phòng cần xoá.

        Returns:
            True nếu xoá thành công.
        """
        await self.db.delete(room)
        await self.db.flush()

    async def get_active_by_cinema(self, cinema_id: UUID) -> list[Rooms]:
        """Lấy danh sách phòng chiếu đang hoạt động trong một cinema.

        Args:
            cinema_id: UUID của cinema.

        Returns:
            Danh sách phòng có is_active = True.
        """
        result = await self.db.execute(
            select(Rooms)
            .where(
                and_(
                    Rooms.cinema_id == cinema_id,
                    col(Rooms.is_active).is_(True)
                )
            )
        )

        return list(result.scalars().all())

    async def count_by_cinema(self, cinema_id: UUID) -> int:
        """Đếm số phòng chiếu trong một cinema.

        Args:
            cinema_id: UUID của cinema.

        Returns:
            Số lượng phòng chiếu.
        """
        count = await self.db.execute(
            select(func.count(Rooms.id))
            .select_from(Rooms)
            .where(Rooms.cinema_id == cinema_id)
        )

        return count.scalar_one()

    async def _update_active_status(self, room_id: UUID, status: bool) -> Rooms | None:
        """Cập nhật trạng thái hoạt động của phòng (internal method).

        Args:
            room_id: UUID của phòng.
            status: Trạng thái mới (True = active, False = inactive).

        Returns:
            Phòng sau khi cập nhật, None nếu không tìm thấy.
        """
        room = await self.get_by_id(room_id)
        if room is None:
            return None

        room.is_active = status
        await self.db.flush()
        await self.db.refresh(room)

        return room

    async def activate(self, room_id: UUID) -> Rooms | None:
        """Kích hoạt phòng chiếu (set is_active = True).

        Args:
            room_id: UUID của phòng.

        Returns:
            Phòng sau khi kích hoạt, None nếu không tìm thấy.
        """
        return await self._update_active_status(room_id, True)

    async def deactivate(self, room_id: UUID) -> Rooms | None:
        """Vô hiệu hoá phòng chiếu (set is_active = False).

        Args:
            room_id: UUID của phòng.

        Returns:
            Phòng sau khi vô hiệu hoá, None nếu không tìm thấy.
        """
        return await self._update_active_status(room_id, False)

    async def get_by_id_with_seats(self, room_id: UUID) -> Rooms | None:
        """Lấy phòng theo ID kèm danh sách ghế (eager loading).

        Args:
            room_id: UUID của phòng.

        Returns:
            Phòng với relationship seats đã được load, None nếu không tìm thấy.
        """
        result = await self.db.execute(
            select(Rooms)
            .where(Rooms.id == room_id)
            .options(
                selectinload(Rooms.seats)
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id_with_showtimes(
        self,
        room_id: UUID,
        target_date: date | None = None,
    ) -> Rooms | None:
        """Lấy phòng theo ID kèm danh sách suất chiếu.

        Có thể filter theo ngày cụ thể.

        Args:
            room_id: UUID của phòng.
            target_date: Ngày cần lọc (optional). Nếu None, lấy tất cả.

        Returns:
            Phòng với showtimes đã eager-load, None nếu không tìm thấy.
        """
        if target_date is None:
            query = (
                select(Rooms)
                .where(Rooms.id == room_id)
                .options(selectinload(Rooms.showtimes))
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        from app.modules.showtimes.models import Showtimes

        join_condition = and_(
            Showtimes.room_id == Rooms.id,
            func.date(Showtimes.start_time) == target_date,
        )
        query = (
            select(Rooms)
            .outerjoin(Showtimes, join_condition)
            .where(Rooms.id == room_id)
            .options(contains_eager(Rooms.showtimes))
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()

    async def exists_by_name_in_cinema(self, cinema_id: UUID, name: str) -> bool:
        """Kiểm tra phòng đã tồn tại trong cinema (case-insensitive).

        Args:
            cinema_id: UUID của cinema.
            name: Tên phòng cần kiểm tra.

        Returns:
            True nếu đã tồn tại, False nếu chưa.
        """
        result = await self.db.execute(
            select(func.count(Rooms.id))
            .where(
                and_(
                    Rooms.cinema_id == cinema_id,
                    func.lower(Rooms.name) == func.lower(name.strip())
                )
            )
        )

        count = result.scalar_one()
        return count > 0


def get_room_repo(
    db: DbSession
) -> RoomRepository:
    """Factory function để tạo RoomRepository (FastAPI dependency).

    Args:
        db: Database session từ dependency injection.

    Returns:
        Instance của RoomRepository.
    """
    return RoomRepository(db)


RoomRepoDep = Annotated[RoomRepository, Depends(get_room_repo)]
