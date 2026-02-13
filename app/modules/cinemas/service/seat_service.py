"""Seat service - business logic for Seat entity."""
from fastapi import Depends
from typing import Annotated
from uuid import UUID
from app.modules.cinemas.repository.seat_repository import SeatRepository, SeatRepoDep
from app.modules.cinemas.repository.room_repository import RoomRepository, RoomRepoDep
from app.modules.cinemas.models import SeatType
from app.modules.cinemas.schemas.domain import (
    SeatDTO, SeatUpdate, BulkSeatUpdate, SeatGenerationConfig, SeatCreate
)
from app.modules.cinemas.exceptions import (
    SeatAlreadyExistsError,
    SeatNotFoundError,
    SeatInactiveError,
    RoomNotFoundError
)


class SeatService:
    """Service xử lý business logic cho Seat."""

    def __init__(self, seat_repo: SeatRepository, room_repo: RoomRepository):
        self.seat_repo = seat_repo
        self.room_repo = room_repo

    async def get_seat(self, seat_id: UUID) -> SeatDTO:
        seat = await self.seat_repo.get_by_id(seat_id)

        if seat is None:
            raise SeatNotFoundError(seat_id)

        return SeatDTO.model_validate(seat)

    async def get_seats_by_room(self, room_id: UUID) -> list[SeatDTO]:
        room = await self.room_repo.get_by_id(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        seats = await self.seat_repo.get_by_room_type(room_id)

        return [SeatDTO.model_validate(seat) for seat in seats]

    async def get_seats_by_type(self, room_id: UUID, seat_type: SeatType) -> list[SeatDTO]:
        room = await self.room_repo.get_by_id(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        seats = await self.seat_repo.get_by_room_type(room_id, seat_type)

        return [SeatDTO.model_validate(seat) for seat in seats]

    async def update_seat(self, seat_id: UUID, data: SeatUpdate) -> SeatDTO:
        seat = await self.seat_repo.get_by_id(seat_id)

        if seat is None:
            raise SeatNotFoundError(seat_id)

        updated_seat = await self.seat_repo.update(seat, data)

        return SeatDTO.model_validate(updated_seat)

    async def bulk_update_seats(self, data: BulkSeatUpdate) -> list[SeatDTO]:
        """Cập nhật loại ghế cho nhiều ghế cùng lúc.

        Validate tất cả seat_ids tồn tại trước khi update.
        """
        seats = await self.seat_repo.get_by_ids(data.seat_ids)

        if len(seats) != len(data.seat_ids):
            found_ids = {s.id for s in seats}
            missing = set(data.seat_ids) - found_ids
            raise SeatNotFoundError(next(iter(missing)))

        # Chỉ update khi có data thực sự
        update_values = {}
        if data.seat_type is not None:
            update_values["seat_type"] = data.seat_type
        if data.price_multiplier is not None:
            update_values["price_multiplier"] = data.price_multiplier

        if not update_values:
            return [SeatDTO.model_validate(seat) for seat in seats]

        updated_seats = await self.seat_repo.bulk_update_type(
            seat_ids=data.seat_ids,
            seat_type=update_values.get("seat_type", seats[0].seat_type),
            price_multiplier=update_values.get(
                "price_multiplier", seats[0].price_multiplier),
        )

        return [SeatDTO.model_validate(seat) for seat in updated_seats]

    async def generate_seats_for_room(
        self,
        room_id: UUID,
        config: SeatGenerationConfig
    ) -> list[SeatDTO]:
        """Reset và tạo lại toàn bộ ghế cho phòng."""
        room = await self.room_repo.get_by_id(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        await self.seat_repo.delete_by_room(room_id)

        seats_data = self._create_seats_from_config(config)
        created_seats = await self.seat_repo.create_many(room_id, seats_data)

        return [SeatDTO.model_validate(seat) for seat in created_seats]

    async def delete_seats_by_room(self, room_id: UUID) -> int:
        room = await self.room_repo.get_by_id(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        return await self.seat_repo.delete_by_room(room_id)

    async def activate_seat(self, seat_id: UUID) -> SeatDTO:
        seat = await self.seat_repo.activate(seat_id)

        if seat is None:
            raise SeatNotFoundError(seat_id)

        return SeatDTO.model_validate(seat)

    async def deactivate_seat(self, seat_id: UUID) -> SeatDTO:
        seat = await self.seat_repo.deactivate(seat_id)

        if seat is None:
            raise SeatNotFoundError(seat_id)

        return SeatDTO.model_validate(seat)

    async def count_seats_by_room(self, room_id: UUID) -> int:
        room = await self.room_repo.get_by_id(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        return await self.seat_repo.count_by_room(room_id)

    def _create_seats_from_config(self, config: SeatGenerationConfig) -> list[SeatCreate]:
        """Sinh danh sách SeatCreate từ SeatGenerationConfig."""
        pattern_map = {
            letter: (pattern.seat_type, pattern.price_multiplier)
            for pattern in config.patterns
            for letter in pattern.row_letters
        }

        default = (config.default_seat_type, config.default_price_multiplier)

        seats: list[SeatCreate] = [
            SeatCreate(
                row_label=chr(ord('A') + row_idx),
                seat_number=seat_num,
                seat_type=pattern_map.get(chr(ord('A') + row_idx), default)[0],
                price_multiplier=pattern_map.get(
                    chr(ord('A') + row_idx), default)[1]
            )
            for row_idx in range(config.total_rows)
            for seat_num in range(1, config.seats_per_row + 1)
        ]

        return seats


def get_seat_service(
    seat_repo: SeatRepoDep,
    room_repo: RoomRepoDep
) -> SeatService:
    return SeatService(seat_repo, room_repo)


SeatServiceDep = Annotated[SeatService, Depends(get_seat_service)]
