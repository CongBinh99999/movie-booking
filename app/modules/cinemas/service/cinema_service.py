"""Cinema service - business logic for Cinema entity."""
from fastapi import Depends
from typing import Annotated
from uuid import UUID
from app.modules.cinemas.repository.cinema_repository import CinemaRepository, CinemaRepoDep
from app.modules.cinemas.schemas.domain import (
    CinemaDTO,
    CinemaSearchCriteria,
    CinemaPaginatedDTO,
    CinemaCreate,
    CinemaUpdate,
    CinemaWithRooms
)
from app.modules.cinemas.exceptions.cinema_exceptions import (
    CinemaAlreadyExistsError,
    CinemaHasRoomsError,
    CinemaInactiveError,
    CinemaNotFoundError
)
from app.shared.schemas.pagination import PaginationParams


class CinemaService:
    """Service xử lý business logic cho Cinema."""

    def __init__(self, cinema_repo: CinemaRepository):
        self.cinema_repo = cinema_repo

    async def get_cinema(self, cinema_id: UUID) -> CinemaDTO:
        cinema = await self.cinema_repo.get_by_id(cinema_id)

        if cinema is None:
            raise CinemaNotFoundError(cinema_id=cinema_id)

        return CinemaDTO.model_validate(cinema)

    async def get_cinemas(self, pagination: PaginationParams) -> CinemaPaginatedDTO:
        cinemas = await self.cinema_repo.get_all(
            skip=pagination.offset,
            limit=pagination.size
        )

        total = await self.cinema_repo.count()
        items = [CinemaDTO.model_validate(cinema) for cinema in cinemas]

        return CinemaPaginatedDTO(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size
        )

    async def get_cinemas_by_city(self, city: str, pagination: PaginationParams) -> CinemaPaginatedDTO:
        cinemas = await self.cinema_repo.get_by_city(
            city=city,
            skip=pagination.offset,
            limit=pagination.size
        )

        total = await self.cinema_repo.count_by_city(city=city)

        items = [CinemaDTO.model_validate(cinema) for cinema in cinemas]

        return CinemaPaginatedDTO(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size
        )

    async def search_cinemas(self, criteria: CinemaSearchCriteria, pagination: PaginationParams) -> list[CinemaDTO]:
        cinemas = await self.cinema_repo.search(
            criteria=criteria,
            skip=pagination.offset,
            limit=pagination.size
        )

        return [CinemaDTO.model_validate(cinema) for cinema in cinemas]

    async def create_cinema(self, data: CinemaCreate) -> CinemaDTO:
        if await self.cinema_repo.exists_by_name_and_city_match(data.name, data.city):
            raise CinemaAlreadyExistsError(data.name)

        cinema = await self.cinema_repo.create(data=data)

        return CinemaDTO.model_validate(cinema)

    async def update_cinema(self, cinema_id: UUID, data: CinemaUpdate) -> CinemaDTO:
        cinema = await self.cinema_repo.get_by_id(cinema_id)

        if cinema is None:
            raise CinemaNotFoundError(cinema_id)

        updated_name = data.name if data.name is not None else cinema.name
        updated_city = data.city if data.city is not None else cinema.city

        if await self.cinema_repo.exists_by_name_and_city_match(
            name=updated_name,
            city=updated_city,
            excluded_cinema_id=cinema_id,
        ):
            raise CinemaAlreadyExistsError(updated_name)

        return CinemaDTO.model_validate(await self.cinema_repo.update(cinema, data))

    async def delete_cinema(self, cinema_id: UUID) -> None:
        cinema = await self.cinema_repo.get_by_id_with_rooms(cinema_id)

        if cinema is None:
            raise CinemaNotFoundError(cinema_id)

        if cinema.rooms:
            raise CinemaHasRoomsError(cinema_id, len(cinema.rooms))

        await self.cinema_repo.delete(cinema_id)

    async def get_cinema_with_rooms(self, cinema_id: UUID) -> CinemaWithRooms:
        cinema = await self.cinema_repo.get_by_id_with_rooms(cinema_id)

        if cinema is None:
            raise CinemaNotFoundError(cinema_id)

        return CinemaWithRooms.model_validate(cinema)

    async def get_cities(self) -> list[str]:
        cities = await self.cinema_repo.get_distinct_cities()

        return cities

    async def activate_cinema(self, cinema_id: UUID) -> CinemaDTO:
        cinema = await self.cinema_repo.activate(cinema_id)

        if cinema is None:
            raise CinemaNotFoundError(cinema_id)

        return CinemaDTO.model_validate(cinema)

    async def deactivate_cinema(self, cinema_id: UUID) -> CinemaDTO:
        cinema = await self.cinema_repo.deactivate(cinema_id)

        if cinema is None:
            raise CinemaNotFoundError(cinema_id)

        return CinemaDTO.model_validate(cinema)


def get_cinema_service(
    cinema_repo: CinemaRepoDep
) -> CinemaService:
    """Factory function để tạo CinemaService (FastAPI dependency)."""
    return CinemaService(cinema_repo)


CinemaServiceDep = Annotated[CinemaService, Depends(get_cinema_service)]
