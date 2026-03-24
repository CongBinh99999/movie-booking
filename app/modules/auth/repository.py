from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, exists
from typing import Annotated
from uuid import UUID

from app.shared.dependencies import DbSession
from app.modules.auth.models import Users, RoleType
from app.modules.auth.schemas.domain import (
    UserCreate,
    UserUpdate
)


class AuthRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Users | None:
        result = await self.db.execute(
            select(Users)
            .where(Users.id == user_id)  # type: ignore[arg-type]
        )

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Users | None:
        result = await self.db.execute(
            select(Users)
            .where(Users.email == email)  # type: ignore[arg-type]
        )

        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Users | None:
        result = await self.db.execute(
            select(Users)
            .where(Users.username == username)  # type: ignore[arg-type]
        )

        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate, hashed_password: str) -> Users:
        user = Users(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def update(self, user: Users, user_data: UserUpdate) -> Users:
        data = user_data.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(user, key, value)

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def delete(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.flush()

        return True

    async def exists_by_email(self, email: str) -> bool:
        result = await self.db.execute(
            select(
                exists().where(Users.email == email)  # type: ignore[arg-type]
            )
        )
        return bool(result.scalar_one())

    async def exists_by_username(self, username: str) -> bool:
        result = await self.db.execute(
            select(
                # type: ignore[arg-type]
                exists().where(Users.username == username)
            )
        )
        return bool(result.scalar_one())

    async def update_password(self, user_id: UUID, hashed_password: str) -> bool:
        user = await self.get_by_id(user_id)

        if not user:
            return False

        user.hashed_password = hashed_password
        await self.db.flush()

        return True

    async def _set_active(self, user_id: UUID, active: bool) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = active
        await self.db.flush()
        return True

    async def activate(self, user_id: UUID) -> bool:
        return await self._set_active(user_id, True)

    async def deactivate(self, user_id: UUID) -> bool:
        return await self._set_active(user_id, False)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Users]:
        result = await self.db.execute(
            select(Users)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def count(self) -> int:
        count = await self.db.execute(
            select(func.count())
            .select_from(Users)
        )

        return count.scalar_one()

    async def get_by_role(self, role: RoleType, skip: int = 0, limit: int = 100) -> list[Users]:
        result = await self.db.execute(
            select(Users)
            .where(Users.role == role)  # type: ignore[arg-type]
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())


def get_auth_repository(
    db: DbSession
) -> AuthRepository:
    return AuthRepository(db)


AuthRepoDep = Annotated[AuthRepository, Depends(get_auth_repository)]
