from app.modules.auth.repository import (
    AuthRepoDep,
    AuthRepository
)

from app.modules.auth.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
    InactiveUserError,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError
)

from app.modules.auth.schemas.domain import (
    UserCreate,
    UserDTO,
    TokenPayload
)

from app.shared.security import (
    hash_password,
    verify_password,
    create_refresh_token,
    create_access_token,
    decode_token
)

from app.modules.auth.token_repository import (
    TokenRepoDep,
    TokenRepository
)

import logging
from typing import Annotated
from fastapi import Depends
from datetime import datetime
from uuid import UUID
from jose import JWTError
from jose.exceptions import ExpiredSignatureError

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        auth_repo: AuthRepository,
        token_repo: TokenRepository
    ):
        self.auth_repo = auth_repo
        self.token_repo = token_repo

    async def register(self, user_data: UserCreate) -> UserDTO:
        if await self.auth_repo.exists_by_email(user_data.email):
            raise EmailAlreadyExistsError()

        if await self.auth_repo.exists_by_username(user_data.username):
            raise UsernameAlreadyExistsError()

        hashed_password = hash_password(user_data.password)

        user = await self.auth_repo.create(user_data, hashed_password)

        return UserDTO.model_validate(user)

    async def login(self, username: str, password: str) -> tuple[str, str, datetime]:
        user = await self.auth_repo.get_by_username(username=username)
        if not user:
            raise UserNotFoundError()

        if not user.is_active:
            raise InactiveUserError()

        valid, new_password = verify_password(
            plain_password=password, hashed_password=user.hashed_password)

        if not valid:
            raise InvalidCredentialsError()

        refresh_token, _, _ = create_refresh_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value}
        )
        access_token, _, access_expires_at = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value}
        )

        return access_token, refresh_token, access_expires_at

    async def logout(self, access_token: str, refresh_token: str | None = None) -> None:
        try:
            access_payload = decode_token(access_token)
            await self.token_repo.blacklist_token(
                jti=access_payload.jti,
                expires_at=access_payload.exp
            )
        except (ExpiredSignatureError, JWTError):
            pass

        if refresh_token:
            try:
                refresh_payload = decode_token(refresh_token)
                await self.token_repo.blacklist_token(
                    jti=refresh_payload.jti,
                    expires_at=refresh_payload.exp
                )
            except (ExpiredSignatureError, JWTError):
                pass

    async def verify_token(self, token: str) -> TokenPayload:
        try:
            payload = decode_token(token)
        except ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError:
            raise InvalidTokenError()

        user = await self.auth_repo.get_by_id(payload.sub)

        if not user or not user.is_active:
            raise InactiveUserError()

        if await self.token_repo.is_blacklisted(payload.jti):
            raise TokenRevokedError()

        return payload

    async def get_authenticated_user(self, token: str) -> UserDTO:
        payload = await self.verify_token(token)
        user = await self.auth_repo.get_by_id(payload.sub)

        if not user:
            raise UserNotFoundError()

        return UserDTO.model_validate(user)

    async def refresh_token(self, refresh_token: str) -> tuple[str, str, datetime]:
        try:
            payload = await self.verify_token(refresh_token)
        except (TokenExpiredError, TokenRevokedError, InactiveUserError, InvalidTokenError):
            raise

        if payload.type != "refresh":
            raise InvalidTokenError()

        access_token, _, access_expires_at = create_access_token(
            subject=str(payload.sub),
            extra_claims={"role": payload.role})

        ref_token, _, _ = create_refresh_token(
            subject=str(payload.sub),
            extra_claims={"role": payload.role})

        return access_token, ref_token, access_expires_at

    async def change_password(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        user = await self.auth_repo.get_by_id(user_id=user_id)

        if user is None:
            raise UserNotFoundError()

        if not user.is_active:
            raise InactiveUserError()

        valid, _ = verify_password(old_password, user.hashed_password)
        if not valid:
            raise InvalidCredentialsError()

        hashed = hash_password(new_password)

        return await self.auth_repo.update_password(user_id=user_id, hashed_password=hashed)


def get_user_service(
    auth_repo: AuthRepoDep,
    token_repo: TokenRepoDep
) -> AuthService:
    return AuthService(auth_repo, token_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_user_service)]
