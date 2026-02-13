"""Room service - business logic for Room entity."""
from fastapi import Depends
from typing import Annotated
from uuid import UUID

from app.modules.cinemas.repository.room_repository import RoomRepository, RoomRepoDep
from app.modules.cinemas.repository.cinema_repository import CinemaRepository, CinemaRepoDep
from app.modules.cinemas.repository.seat_repository import SeatRepository, SeatRepoDep
from app.modules.cinemas.schemas.domain import (
    RoomDTO, RoomCreate, RoomUpdate, RoomWithSeats,
    SeatCreate, SeatPattern, SeatGenerationConfig, SeatDTO
)
from app.modules.cinemas.exceptions.room_exceptions import (
    RoomNotFoundError,
    RoomAlreadyExistsError,
    RoomInactiveError,
    RoomHasShowtimesError,
)
from app.modules.cinemas.exceptions.cinema_exceptions import CinemaNotFoundError
from app.shared.schemas.pagination import PaginationParams


class RoomService:
    """Service xử lý business logic cho Room."""

    def __init__(
        self,
        room_repo: RoomRepository,
        cinema_repo: CinemaRepository,
        seat_repo: SeatRepository
    ):
        self.room_repo = room_repo
        self.cinema_repo = cinema_repo
        self.seat_repo = seat_repo

    async def get_room(self, room_id: UUID) -> RoomDTO:
        room = await self.room_repo.get_by_id(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        return RoomDTO.model_validate(room)

    async def get_rooms_by_cinema(self, cinema_id: UUID, pagination: PaginationParams) -> list[RoomDTO]:
        if await self.cinema_repo.get_by_id(cinema_id) is None:
            raise CinemaNotFoundError(cinema_id)

        rooms = await self.room_repo.get_by_cinema(cinema_id, pagination.offset, pagination.size)

        return [RoomDTO.model_validate(room) for room in rooms]

    async def get_active_rooms_by_cinema(self, cinema_id: UUID) -> list[RoomDTO]:
        if await self.cinema_repo.get_by_id(cinema_id) is None:
            raise CinemaNotFoundError(cinema_id)

        rooms = await self.room_repo.get_active_by_cinema(cinema_id)

        return [RoomDTO.model_validate(room) for room in rooms]

    async def create_room(self, cinema_id: UUID, data: RoomCreate) -> RoomDTO:
        if await self.cinema_repo.get_by_id(cinema_id) is None:
            raise CinemaNotFoundError(cinema_id)

        if await self.room_repo.exists_by_name_in_cinema(cinema_id, data.name):
            raise RoomAlreadyExistsError(data.name)

        room = await self.room_repo.create(cinema_id, data)

        config = SeatGenerationConfig(
            total_rows=data.total_rows,
            seats_per_row=data.seats_per_row,
            patterns=data.patterns or [],
        )

        seats_data = self._generate_seats_data(config)

        await self.seat_repo.create_many(room.id, seats_data)

        return RoomDTO.model_validate(room)

    def _generate_seats_data(self, config: SeatGenerationConfig) -> list[SeatCreate]:
        """Sinh danh sách SeatCreate từ SeatGenerationConfig.

        Quy tắc:
        - Nếu hàng nằm trong patterns → dùng seat_type/price từ pattern.
        - Nếu không → dùng default (STANDARD, 1.0).
        """
        seats: list[SeatCreate] = []

        # Build lookup map: {"A": pattern, "B": pattern, ...}
        pattern_map: dict[str, SeatPattern] = {}
        for pattern in config.patterns:
            for letter in pattern.row_letters:
                pattern_map[letter] = pattern

        for row_index in range(config.total_rows):
            row_label = chr(ord('A') + row_index)

            if row_label in pattern_map:
                seat_type = pattern_map[row_label].seat_type
                price_multiplier = pattern_map[row_label].price_multiplier
            else:
                seat_type = config.default_seat_type
                price_multiplier = config.default_price_multiplier

            for seat_num in range(1, config.seats_per_row + 1):
                seats.append(
                    SeatCreate(
                        row_label=row_label,
                        seat_number=seat_num,
                        seat_type=seat_type,
                        price_multiplier=price_multiplier,
                    )
                )

        return seats

    async def update_room(self, room_id: UUID, data: RoomUpdate) -> RoomDTO:
        room = await self.room_repo.get_by_id(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        room = await self.room_repo.update(room, data)

        return RoomDTO.model_validate(room)

    async def delete_room(self, room_id: UUID) -> None:
        """Xoá phòng chiếu.

        Cần eager load showtimes để kiểm tra trước khi xoá.
        """
        room = await self.room_repo.get_by_id_with_showtimes(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        if room.showtimes:
            raise RoomHasShowtimesError(room_id, len(room.showtimes))

        await self.room_repo.delete(room)

    async def get_room_with_seats(self, room_id: UUID) -> RoomWithSeats:
        """Lấy phòng kèm danh sách ghế để hiển thị sơ đồ."""
        room = await self.room_repo.get_by_id_with_seats(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        return RoomWithSeats.model_validate(room)

    async def activate_room(self, room_id: UUID) -> RoomDTO:
        """Kích hoạt phòng chiếu."""
        room = await self.room_repo.activate(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        return RoomDTO.model_validate(room)

    async def deactivate_room(self, room_id: UUID) -> RoomDTO:
        """Vô hiệu hoá phòng chiếu."""
        room = await self.room_repo.deactivate(room_id)

        if room is None:
            raise RoomNotFoundError(room_id)

        return RoomDTO.model_validate(room)


def get_room_service(
    room_repo: RoomRepoDep,
    cinema_repo: CinemaRepoDep,
    seat_repo: SeatRepoDep
) -> RoomService:
    return RoomService(room_repo, cinema_repo, seat_repo)


RoomServiceDep = Annotated[RoomService, Depends(get_room_service)]
