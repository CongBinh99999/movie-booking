# Backend — FastAPI + uv
#
# Tách hai tầng: tầng deps chỉ phụ thuộc pyproject.toml + uv.lock nên sửa code
# không phải cài lại thư viện. Tầng runtime không mang theo uv hay cache.

FROM python:3.13-slim AS deps

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# --frozen: cài đúng uv.lock, không tự resolve lại. Lock đổi mà quên commit thì
# build fail ngay, thay vì lặng lẽ cài phiên bản khác trên máy khác.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM python:3.13-slim AS runtime

# PYTHONPATH: uvicorn và alembic tự chèn cwd vào sys.path, script chạy rời thì
# không — khai rõ để `docker compose exec backend python ...` cũng import được.
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY --from=deps /opt/venv /opt/venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

# Không chạy bằng root.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Migration chạy trước khi mở cổng: container lên thì schema đã đúng.
# Alembic tự idempotent nên khởi động lại nhiều lần vẫn an toàn.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
