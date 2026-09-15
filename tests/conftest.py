"""Fixture dùng chung.

Test tích hợp cần Postgres thật; đặt ``TEST_DATABASE_URL`` để bật. Không đặt
thì chúng tự skip, unit test vẫn chạy bình thường ở mọi máy.

    TEST_DATABASE_URL=postgresql+asyncpg://postgres:pw@localhost:5432/mb_test pytest
"""
import os
import subprocess
import sys

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("VNPAY_TMN_CODE", "TESTCODE")  # VNPay cấp mã đúng 8 ký tự
os.environ.setdefault("VNPAY_HASH_SECRET", "test")
os.environ.setdefault("APP_DEBUG", "false")

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
# app.shared.database dựng engine lúc import, nên phải trỏ DATABASE_URL sang DB
# test TRƯỚC khi bất kỳ module app nào được import.
if TEST_DATABASE_URL:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest.fixture(scope="session")
def migrated_db() -> str:
    """Chạy alembic lên DB test một lần cho cả session."""
    if not TEST_DATABASE_URL:
        pytest.skip("cần TEST_DATABASE_URL để chạy test tích hợp")

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"không chạy được migration lên DB test:\n{result.stderr[-500:]}")

    return TEST_DATABASE_URL


TABLES = (
    "users, movies, genres, movie_genres, cinemas, rooms, "
    "seats, showtimes, bookings, booking_seats, payments"
)


@pytest.fixture
async def session(migrated_db):
    """AsyncSession sạch; xoá sạch bảng sau mỗi test."""
    from sqlalchemy import text
    from app.shared.database import AsyncSessionLocal, engine
    import app.shared.models_registry  # noqa: F401

    async with AsyncSessionLocal() as db:
        yield db

    async with AsyncSessionLocal() as db:
        await db.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))
        await db.commit()

    # pytest-asyncio dựng event loop mới cho mỗi test, mà connection asyncpg thì
    # gắn với loop đã tạo ra nó. Không dispose thì test sau mượn phải connection
    # của loop đã đóng.
    await engine.dispose()
