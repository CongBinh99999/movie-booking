"""Regression test cho 3 lỗi bảo mật của AuthService."""
from uuid import uuid4

import pytest

from app.modules.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from app.modules.auth.models import RoleType
from app.modules.auth.service import AuthService
from app.shared.security import create_access_token, create_refresh_token, hash_password


class FakeUser:
    def __init__(self, password: str = "correct-horse", is_active: bool = True):
        self.id = uuid4()
        self.username = "alice"
        self.hashed_password = hash_password(password)
        self.is_active = is_active
        self.role = RoleType.USER


class FakeAuthRepo:
    def __init__(self, user: FakeUser | None):
        self.user = user

    async def get_by_username(self, username: str):
        return self.user if self.user and self.user.username == username else None

    async def get_by_id(self, user_id):
        return self.user


class FakeTokenRepo:
    def __init__(self):
        self.blacklist: set[str] = set()

    async def blacklist_token(self, jti: str, expires_at) -> bool:
        self.blacklist.add(jti)
        return True

    async def is_blacklisted(self, jti: str) -> bool:
        return jti in self.blacklist


def build_service(user: FakeUser | None = None):
    token_repo = FakeTokenRepo()
    return AuthService(FakeAuthRepo(user), token_repo), token_repo


@pytest.mark.asyncio
async def test_refresh_token_khong_dung_duoc_lam_access_token():
    user = FakeUser()
    service, _ = build_service(user)
    refresh, _, _ = create_refresh_token(subject=str(user.id), extra_claims={"role": "user"})

    with pytest.raises(InvalidTokenError):
        await service.verify_token(refresh)

    # access token thì vẫn phải qua
    access, _, _ = create_access_token(subject=str(user.id), extra_claims={"role": "user"})
    assert (await service.verify_token(access)).type == "access"


@pytest.mark.asyncio
async def test_xoay_refresh_token_thu_hoi_token_cu():
    user = FakeUser()
    service, token_repo = build_service(user)
    refresh, old_jti, _ = create_refresh_token(
        subject=str(user.id), extra_claims={"role": "user"}
    )

    await service.refresh_token(refresh)

    assert old_jti in token_repo.blacklist
    with pytest.raises(Exception):  # TokenRevokedError
        await service.refresh_token(refresh)


@pytest.mark.asyncio
async def test_login_sai_username_va_sai_password_cho_cung_mot_loi():
    user = FakeUser(password="correct-horse")

    service_khong_co_user, _ = build_service(None)
    with pytest.raises(InvalidCredentialsError):
        await service_khong_co_user.login("bob", "bat-ky")

    service_co_user, _ = build_service(user)
    with pytest.raises(InvalidCredentialsError):
        await service_co_user.login("alice", "sai-mat-khau")

    # mật khẩu đúng thì vẫn đăng nhập được
    access, refresh, _ = await service_co_user.login("alice", "correct-horse")
    assert access and refresh
