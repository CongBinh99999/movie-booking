"""Test cho vòng lặp nền dọn booking hết hạn.

Phần nghiệp vụ (`expire_pending_bookings`) đã có test riêng; ở đây chỉ chốt
hai hành vi mới của task: khoá chống chạy trùng, và vòng lặp không chết vì lỗi.
"""
import asyncio

import pytest

from app.modules.bookings import tasks


class FakeRedis:
    """Chỉ đủ cho SET NX EX."""

    def __init__(self):
        self.keys: set[str] = set()

    async def set(self, key, value, nx=False, ex=None):
        if nx and key in self.keys:
            return None
        self.keys.add(key)
        return True


@pytest.mark.asyncio
async def test_lock_chan_luot_chay_trung(monkeypatch):
    """Worker thứ hai trong cùng một chu kỳ phải bỏ lượt, không dọn chồng lên nhau."""
    redis = FakeRedis()
    calls = []

    monkeypatch.setattr(tasks, "get_redis_client", _ctx(redis))
    monkeypatch.setattr(tasks, "AsyncSessionLocal", _ctx(_FakeSession()))
    monkeypatch.setattr(tasks, "BookingService", _service_stub(calls))
    for name in ("BookingRepository", "BookingSeatRepository", "ShowtimeRepository", "SeatRepository"):
        monkeypatch.setattr(tasks, name, lambda _s: None)

    assert await tasks.expire_bookings_once() == 3
    assert await tasks.expire_bookings_once() == 0  # khoá còn giữ
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_vong_lap_song_sot_qua_loi(monkeypatch):
    """Một lượt lỗi không được giết cả vòng lặp."""
    ket_qua = [RuntimeError("db down"), 1]
    da_chay = []

    async def fake_once():
        value = ket_qua[len(da_chay)] if len(da_chay) < len(ket_qua) else 0
        da_chay.append(value)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(tasks, "expire_bookings_once", fake_once)
    monkeypatch.setattr(tasks, "EXPIRE_INTERVAL_SECONDS", 0)

    task = asyncio.create_task(tasks.expire_bookings_loop())
    while len(da_chay) < 2:
        await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert isinstance(da_chay[0], RuntimeError)  # lượt đầu lỗi
    assert da_chay[1] == 1                        # vẫn chạy lượt sau


# --- helper ---

def _ctx(obj):
    class _Ctx:
        async def __aenter__(self):
            return obj

        async def __aexit__(self, *_):
            return False

    return lambda: _Ctx()


class _FakeSession:
    async def commit(self):
        return None


def _service_stub(calls):
    class _Service:
        def __init__(self, **kwargs):
            pass

        async def expire_pending_bookings(self):
            calls.append(1)
            return 3

    return _Service
