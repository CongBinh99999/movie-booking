"""Helper dựng dữ liệu mẫu cho test tích hợp."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.modules.auth.models import RoleType, Users
from app.modules.bookings.models import Bookings, BookingSeats, BookingStatus
from app.modules.cinemas.models import Cinemas, Rooms, Seats, SeatType
from app.modules.movies.models import Movies
from app.modules.showtimes.models import Showtimes


def now() -> datetime:
    return datetime.now(timezone.utc)


async def make_user(session, username="alice", hashed_password="x", role=RoleType.USER):
    user = Users(
        email=f"{username}@example.com", username=username,
        hashed_password=hashed_password, role=role,
    )
    session.add(user)
    await session.flush()
    return user


async def make_room(session, name="R1"):
    cinema = Cinemas(name="CGV", address="1 Main St", city="HN")
    session.add(cinema)
    await session.flush()

    room = Rooms(cinema_id=cinema.id, name=name, total_rows=1,
                 seats_per_row=10, total_seats=10)
    session.add(room)
    await session.flush()
    return cinema, room


async def make_seats(session, room, count=2):
    seats = [
        Seats(room_id=room.id, row_label="A", seat_number=i + 1,
              seat_type=SeatType.STANDARD, price_multiplier=Decimal("1.00"))
        for i in range(count)
    ]
    session.add_all(seats)
    await session.flush()
    return seats


async def make_showtime(session, room, hours_ahead=2, base_price="100000"):
    movie = Movies(title="Dune", original_title="Dune", duration_minutes=155,
                   release_date=now().date() - timedelta(days=1), is_active=True)
    session.add(movie)
    await session.flush()

    showtime = Showtimes(
        movie_id=movie.id, room_id=room.id,
        start_time=now() + timedelta(hours=hours_ahead),
        end_time=now() + timedelta(hours=hours_ahead + 2),
        base_price=Decimal(base_price), is_active=True,
    )
    session.add(showtime)
    await session.flush()
    return movie, showtime


async def make_booking(session, user, showtime, seats, *, expires_in_minutes=15,
                       status=BookingStatus.PENDING, code="BK0001"):
    booking = Bookings(
        user_id=user.id, showtime_id=showtime.id, booking_code=code,
        status=status, total_amount=Decimal("100000") * len(seats),
        expires_at=now() + timedelta(minutes=expires_in_minutes),
    )
    session.add(booking)
    await session.flush()
    session.add_all([
        BookingSeats(booking_id=booking.id, seat_id=s.id, price=Decimal("100000"))
        for s in seats
    ])
    await session.flush()
    return booking
