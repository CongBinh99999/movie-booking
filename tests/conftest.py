"""Env tối thiểu để import được app.core.config (JWT_SECRET và VNPAY_* là field bắt buộc)."""
import os

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("VNPAY_TMN_CODE", "test")
os.environ.setdefault("VNPAY_HASH_SECRET", "test")
