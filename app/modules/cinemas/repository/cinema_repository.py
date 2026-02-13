from fastapi import Depends
from app.shared.dependencies import DbSession
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.modules.cinemas.models import Cinemas
from uuid import UUID
from sqlalchemy import select, func, update, and_
from sqlmodel import col
from sqlalchemy.orm import selectinload
from app.modules.cinemas.schemas.domain import CinemaCreate, CinemaUpdate, CinemaSearchCriteria


class CinemaRepository:
    """Repository xử lý các thao tác CRUD cho entity Cinema."""

    def __init__(self, db: AsyncSession):
        """Khởi tạo repository với database session.

        Args:
            db: AsyncSession kết nối với database.
        """
        self.db = db

    async def get_by_id(self, cinema_id: UUID) -> Cinemas | None:
        """Lấy cinema theo ID.

        Args:
            cinema_id: UUID của cinema cần tìm.

        Returns:
            Cinemas nếu tìm thấy, None nếu không tồn tại.
        """
        result = await self.db.execute(
            select(Cinemas)
            .where(Cinemas.id == cinema_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Cinemas]:
        """Lấy danh sách tất cả cinema với phân trang.

        Args:
            skip: Số lượng bản ghi bỏ qua (mặc định 0).
            limit: Số lượng bản ghi tối đa trả về (mặc định 100).

        Returns:
            Danh sách các cinema, sắp xếp theo tên.
        """
        result = await self.db.execute(
            select(Cinemas)
            .order_by(Cinemas.name)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def create(self, data: CinemaCreate) -> Cinemas:
        """Tạo mới một cinema.

        Args:
            data: Dữ liệu cinema cần tạo.

        Returns:
            Cinema vừa được tạo với ID được generate.
        """
        cinema = Cinemas(
            name=data.name,
            address=data.address,
            city=data.city,
            district=data.district,
            phone=data.phone,
            email=data.email,
            description=data.description,
            image_url=data.image_url,
            latitude=data.latitude,
            longitude=data.longitude
        )

        self.db.add(cinema)

        await self.db.flush()
        await self.db.refresh(cinema)

        return cinema

    async def update(self, cinema: Cinemas, updated_data: CinemaUpdate) -> Cinemas:
        """Cập nhật thông tin cinema.

        Chỉ cập nhật các field được truyền vào (exclude_unset=True).

        Args:
            cinema: Entity cinema cần cập nhật.
            updated_data: Dữ liệu cập nhật (partial update).

        Returns:
            Cinema sau khi cập nhật.
        """
        data = updated_data.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(cinema, key, value)

        await self.db.flush()
        await self.db.refresh(cinema)
        return cinema

    async def delete(self, cinema_id: UUID) -> bool:
        """Xoá cinema theo ID (hard delete).

        Args:
            cinema_id: UUID của cinema cần xoá.

        Returns:
            True nếu xoá thành công, False nếu không tìm thấy cinema.
        """
        cinema = await self.get_by_id(cinema_id)

        if cinema is None:
            return False

        await self.db.delete(cinema)
        await self.db.flush()

        return True

    async def get_by_city(self, city: str, skip: int = 0, limit: int = 100) -> list[Cinemas]:
        """Lấy danh sách cinema theo thành phố.

        Args:
            city: Tên thành phố cần lọc.
            skip: Số lượng bản ghi bỏ qua.
            limit: Số lượng bản ghi tối đa.

        Returns:
            Danh sách cinema thuộc thành phố được chỉ định.
        """
        result = await self.db.execute(
            select(Cinemas)
            .where(Cinemas.city == city)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[Cinemas]:
        """Lấy danh sách cinema đang hoạt động.

        Args:
            skip: Số lượng bản ghi bỏ qua.
            limit: Số lượng bản ghi tối đa.

        Returns:
            Danh sách cinema có is_active = True.
        """
        result = await self.db.execute(
            select(Cinemas)
            .where(col(Cinemas.is_active).is_(True))
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    def _escape_like_pattern(self, pattern: str) -> str:
        """Escape ký tự đặc biệt trong LIKE pattern để tránh SQL injection.

        Args:
            pattern: Chuỗi cần escape.

        Returns:
            Chuỗi đã được escape các ký tự \\, %, _.
        """
        return (pattern
                .replace("\\", "\\\\")
                .replace("%", r"\%")
                .replace("_", r"\_"))
    
    def _build_search_conditions(self, criteria: CinemaSearchCriteria) -> list: 
        conditions = []
        
        if criteria.city:
            conditions.append(func.lower(Cinemas.city) == criteria.city.strip().lower())

        if criteria.district:
            conditions.append(func.lower(Cinemas.district) == criteria.district.strip().lower())

        if criteria.name_contains:
            escaped = self._escape_like_pattern(criteria.name_contains.strip())
            conditions.append(col(Cinemas.name).ilike(f"%{escaped}%", escape="\\"))

        if criteria.is_active is not None:
            conditions.append(col(Cinemas.is_active).is_(criteria.is_active))

        if criteria.lat_min is not None:
            conditions.append(Cinemas.latitude >= criteria.lat_min)
        if criteria.lat_max is not None:
            conditions.append(Cinemas.latitude <= criteria.lat_max)

        if criteria.lng_min is not None:
            conditions.append(Cinemas.longitude >= criteria.lng_min)
        if criteria.lng_max is not None:
            conditions.append(Cinemas.longitude <= criteria.lng_max)

        return conditions

    async def search(self, criteria: CinemaSearchCriteria, skip: int = 0, limit: int = 20) -> list[Cinemas]: 
        query = select(Cinemas)
        conditions = self._build_search_conditions(criteria)
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Cinemas.city, Cinemas.name).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_search(self, criteria: CinemaSearchCriteria) -> int:
        query = select(func.count(Cinemas.id)).select_from(Cinemas)
        conditions = self._build_search_conditions(criteria)
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def count(self) -> int:
        """Đếm tổng số cinema trong database.

        Returns:
            Số lượng cinema.
        """
        count = await self.db.execute(
            select(func.count(Cinemas.id)).select_from(Cinemas)
        )

        return count.scalar_one()

    async def count_by_city(self, city: str) -> int:
        """Đếm số cinema theo thành phố.

        Args:
            city: Tên thành phố.

        Returns:
            Số lượng cinema trong thành phố.
        """
        count = await self.db.execute(
            select(func.count(Cinemas.id))
            .select_from(Cinemas)
            .where(Cinemas.city == city)
        )

        return count.scalar_one()

    async def _update_active_status(self, cinema_id: UUID, status: bool) -> Cinemas | None:
        """Cập nhật trạng thái hoạt động của cinema (internal method).

        Args:
            cinema_id: UUID của cinema.
            status: Trạng thái mới (True = active, False = inactive).

        Returns:
            Cinema sau khi cập nhật, None nếu không tìm thấy.
        """
        cinema = await self.get_by_id(cinema_id)
        if cinema is None:
            return None

        cinema.is_active = status
        await self.db.flush()
        await self.db.refresh(cinema)

        return cinema

    async def activate(self, cinema_id: UUID) -> Cinemas | None:
        """Kích hoạt cinema (set is_active = True).

        Args:
            cinema_id: UUID của cinema.

        Returns:
            Cinema sau khi kích hoạt, None nếu không tìm thấy.
        """
        return await self._update_active_status(cinema_id, True)

    async def deactivate(self, cinema_id: UUID) -> Cinemas | None:
        """Vô hiệu hoá cinema (set is_active = False).

        Args:
            cinema_id: UUID của cinema.

        Returns:
            Cinema sau khi vô hiệu hoá, None nếu không tìm thấy.
        """
        return await self._update_active_status(cinema_id, False)

    async def get_by_id_with_rooms(self, cinema_id: UUID) -> Cinemas | None:
        """Lấy cinema theo ID kèm theo danh sách phòng chiếu (eager loading).

        Args:
            cinema_id: UUID của cinema.

        Returns:
            Cinema với relationship rooms đã được load, None nếu không tìm thấy.
        """
        result = await self.db.execute(
            select(Cinemas)
            .where(Cinemas.id == cinema_id)
            .options(
                selectinload(Cinemas.rooms)
            )
        )

        return result.scalar_one_or_none()

    async def exists_by_name_and_city_match(self, name: str, city: str, excluded_cinema_id: UUID | None = None) -> bool:
        query = (
            select(Cinemas)
            .where(
                and_(
                    func.lower(Cinemas.name) == func.lower(name.strip()),
                    func.lower(Cinemas.city) == func.lower(city.strip())
                )
            )
        )
        if excluded_cinema_id: 
            query = query.where(and_(Cinemas.id != excluded_cinema_id))
        
        query = query.limit(1)

        exists = await self.db.execute(query)
        
        return exists.scalar_one_or_none() is not None

    async def get_distinct_cities(self) -> list[str]:
        """Lấy danh sách các thành phố có cinema.

        Returns:
            Danh sách tên thành phố (không trùng lặp).
        """
        result = await self.db.execute(
            select(Cinemas.city)
            .distinct()
        )

        return list(result.scalars().all())


def get_cinema_repository(
    db: DbSession
) -> CinemaRepository:
    """Factory function để tạo CinemaRepository (FastAPI dependency).

    Args:
        db: Database session từ dependency injection.

    Returns:
        Instance của CinemaRepository.
    """
    return CinemaRepository(db)


CinemaRepoDep = Annotated[CinemaRepository, Depends(get_cinema_repository)]
