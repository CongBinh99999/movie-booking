"""Smoke test qua HTTP: mọi router có gắn đúng và luồng auth chạy được đầu-cuối."""
import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient

from app.shared.database import get_db
from app.shared.redis import get_redis

CREDS = {"username": "smokeuser", "password": "Str0ng-Passw0rd!"}


@pytest.fixture
async def client(session):
    """Client ASGI dùng chung session của test, nên dữ liệu được dọn sau mỗi test.

    Redis thay bằng fakeredis: suite không cần server Redis để chạy.
    """
    from app.main import app

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async def override_get_db():
        yield session

    async def override_get_redis():
        yield fake_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as c:
        yield c
    app.dependency_overrides.clear()


async def register_and_login(client) -> dict:
    resp = await client.post("/auth/register", json={
        "email": "smoke@example.com", "username": CREDS["username"],
        "password": CREDS["password"], "confirmed_password": CREDS["password"],
        "full_name": "Smoke User",
    })
    assert resp.status_code in (200, 201), resp.text

    resp = await client.post("/auth/login", data=CREDS)
    assert resp.status_code == 200, resp.text
    return resp.json()


async def test_dang_ky_dang_nhap_va_lay_thong_tin(client):
    tokens = await register_and_login(client)
    assert tokens["access_token"] and tokens["refresh_token"]

    me = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert me.status_code == 200

    body = me.json()
    assert set(body) == {
        "id", "email", "username", "full_name", "role", "is_active",
        "created_at", "updated_at",
    }
    assert body["username"] == CREDS["username"]
    assert body["email"] == "smoke@example.com"
    assert body["role"] == "user"
    assert "hashed_password" not in body


async def test_refresh_token_khong_dung_duoc_o_endpoint_thuong(client):
    """Chốt lại lỗ hổng đã vá: refresh token sống 7 ngày, không được thay access token."""
    tokens = await register_and_login(client)

    resp = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
    )
    assert resp.status_code == 401


async def test_sai_username_va_sai_password_tra_cung_mot_loi(client):
    await register_and_login(client)

    khong_ton_tai = await client.post(
        "/auth/login", data={"username": "nobody", "password": "whatever"}
    )
    sai_mat_khau = await client.post(
        "/auth/login", data={"username": CREDS["username"], "password": "wrong"}
    )

    assert khong_ton_tai.status_code == sai_mat_khau.status_code == 401
    assert khong_ton_tai.json()["error_code"] == sai_mat_khau.json()["error_code"]


async def test_endpoint_can_dang_nhap_tu_choi_khach(client):
    assert (await client.get("/bookings")).status_code == 401


async def test_endpoint_cong_khai_mo_cho_khach(client):
    for path in ("/movies", "/genres", "/showtimes", "/cinemas"):
        resp = await client.get(path)
        assert resp.status_code == 200, f"{path} -> {resp.status_code} {resp.text[:200]}"
