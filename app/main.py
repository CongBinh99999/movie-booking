from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.shared.database import init_db
from app.core.config import get_setting
from app.shared.exceptions import AppException

from app.modules.auth.router import router as auth_router
from app.modules.bookings.router import (
    booking_router, booking_seat_router, admin_booking_router,
)
from app.modules.cinemas.router import (
    cinema_router, room_router, seat_router,
    cinema_rooms_router, room_seats_router,
)
from app.modules.movies.router import movie_router, genre_router
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


# Auth
app.include_router(auth_router, prefix="/api/v1")

# Movies
app.include_router(movie_router, prefix="/api/v1")
app.include_router(genre_router, prefix="/api/v1")

# Cinemas
app.include_router(cinema_router, prefix="/api/v1")
app.include_router(room_router, prefix="/api/v1")
app.include_router(seat_router, prefix="/api/v1")
app.include_router(cinema_rooms_router, prefix="/api/v1")
app.include_router(room_seats_router, prefix="/api/v1")

# Bookings
app.include_router(booking_router, prefix="/api/v1")
app.include_router(booking_seat_router, prefix="/api/v1")
app.include_router(admin_booking_router, prefix="/api/v1")

# Showtimes
app.include_router(showtimes_router, prefix="/api/v1")

# Payments
app.include_router(payments_router, prefix="/api/v1")
