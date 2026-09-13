"""Import mọi module trong app/ — không cần DB, Redis hay mạng.

Lỗ hổng thật đã xảy ra: một import bị xoá nhầm khiến `import app.main` ném
NameError, mà suite vẫn xanh — unit test không chạm app.main, còn smoke test
thì skip khi thiếu TEST_DATABASE_URL. Test này bịt đúng chỗ đó.
"""
import importlib
import pkgutil

import pytest

MODULES = sorted(m.name for m in pkgutil.walk_packages(["app"], prefix="app."))


def test_tim_thay_module():
    assert len(MODULES) > 50, MODULES


@pytest.mark.parametrize("module", MODULES)
def test_import_duoc(module):
    importlib.import_module(module)


def test_app_dung_duoc_openapi():
    """Bắt cả lỗi khai báo route/schema mà import đơn thuần không lộ ra."""
    from app.main import app

    spec = app.openapi()
    endpoints = sum(
        len([m for m in v if m in ("get", "post", "put", "patch", "delete")])
        for v in spec["paths"].values()
    )
    assert endpoints > 60, endpoints
