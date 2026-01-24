from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.shared.database import init_db
from app.core.config import get_setting
from app.shared.exceptions import AppException

from app.modules.auth.router import router as auth_router
from app.modules.bookings.router import router as bookings_router
from app.modules.cinemas.router import router as cinemas_router
from app.modules.movies.router import router as movies_router
from app.modules.payments.router import router as payments_router
from app.modules.showtimes.router import router as showtimes_router


setting = get_setting()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Khởi động")
    await init_db()
    yield
    print("Shutdown")


app = FastAPI(
    title=setting.APP_NAME,
    version=setting.APP_VERSION,
    debug=setting.APP_DEBUG,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


app.include_router(auth_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(cinemas_router, prefix="/api/v1")
app.include_router(movies_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(showtimes_router, prefix="/api/v1")
