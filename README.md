# 🎬 Movie Booking

Hệ thống đặt vé xem phim trực tuyến — Full-stack với **FastAPI** (Backend) và **Next.js** (Frontend).

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework (async) |
| **SQLModel + SQLAlchemy** | ORM (async với `asyncpg`) |
| **PostgreSQL** | Database chính |
| **Redis** | Seat locking, caching |
| **Pydantic v2** | Schema validation |
| **JWT (jose) + Argon2** | Authentication & password hashing |
| **VNPay SDK** | Payment gateway |
| **Alembic** | Database migrations |

### Frontend

| Technology | Purpose |
|---|---|
| **Next.js 16** | React framework (App Router) |
| **React 19** | UI library |
| **TanStack Query v5** | Server state management |
| **Zustand** | Client state management |
| **Tailwind CSS v4** | Styling |
| **React Hook Form + Zod** | Form handling & validation |
| **Axios** | HTTP client |

## Project Structure

```
movie_booking/
├── app/                          # Backend (FastAPI)
│   ├── core/                     # Config (pydantic-settings)
│   ├── shared/                   # Database, Redis, Security, Exceptions
│   │   ├── database.py           # Async SQLAlchemy engine & session
│   │   ├── security.py           # JWT tokens & password hashing
│   │   ├── redis.py              # Redis connection pool
│   │   ├── exceptions.py         # Custom exception hierarchy
│   │   └── dependencies.py       # FastAPI DI (DbSession, RedisClient)
│   └── modules/
│       ├── auth/                  # Register, Login, JWT refresh, Change password
│       ├── movies/                # Movies & Genres CRUD
│       ├── cinemas/               # Cinemas, Rooms & Seats management
│       ├── bookings/              # Booking flow, seat availability, admin ops
│       ├── showtimes/             # Showtime scheduling (CRUD + bulk create)
│       └── payments/              # VNPay integration (create, IPN, verify)
├── frontend/                     # Frontend (Next.js)
│   └── src/
│       ├── app/                  # Pages (auth, booking, movies)
│       ├── components/           # Reusable UI components
│       ├── hooks/                # Custom React hooks
│       ├── services/             # API service layer
│       ├── store/                # Zustand stores
│       └── types/                # TypeScript types
├── database/
│   └── schema.sql                # Full database schema
├── alembic/                      # Database migrations
├── tests/                        # Test suite (pytest, async)
├── scripts/                      # Utility scripts
└── docs/                         # Documentation
```

## API Endpoints

**Base URL:** `/api/v1`

### Authentication (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Đăng ký tài khoản |
| POST | `/auth/login` | Đăng nhập (OAuth2 form) |
| POST | `/auth/logout` | Đăng xuất |
| POST | `/auth/refresh` | Refresh token |
| GET | `/auth/me` | Thông tin người dùng |
| POST | `/auth/me/change-password` | Đổi mật khẩu |

### Movies (`/movies`, `/genres`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/movies` | Danh sách phim |
| GET | `/movies/{id}` | Chi tiết phim |
| POST | `/movies` | Tạo phim (Admin) |
| PUT | `/movies/{id}` | Cập nhật phim (Admin) |
| DELETE | `/movies/{id}` | Xóa phim (Admin) |
| GET | `/genres` | Danh sách thể loại |
| POST | `/genres` | Tạo thể loại (Admin) |

### Cinemas (`/cinemas`, `/rooms`, `/seats`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cinemas` | Danh sách rạp |
| POST | `/cinemas` | Tạo rạp (Admin) |
| GET | `/cinemas/{id}/rooms` | Danh sách phòng chiếu |
| POST | `/rooms` | Tạo phòng chiếu (Admin) |
| GET | `/rooms/{id}/seats` | Danh sách ghế |
| POST | `/seats` | Tạo ghế (Admin) |

### Bookings (`/bookings`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bookings` | Tạo đơn đặt vé |
| GET | `/bookings` | Danh sách đơn đặt vé |
| POST | `/bookings/calculate` | Tính giá đặt vé |
| GET | `/bookings/code/{code}` | Tra cứu theo mã |
| GET | `/bookings/{id}` | Chi tiết đơn đặt vé |
| POST | `/bookings/{id}/cancel` | Hủy đơn đặt vé |
| GET | `/showtimes/{id}/seats` | Ghế khả dụng theo suất chiếu |
| GET | `/admin/bookings` | [Admin] Danh sách tất cả đơn |
| PATCH | `/admin/bookings/{id}/status` | [Admin] Cập nhật trạng thái |

### Showtimes (`/showtimes`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/showtimes` | Danh sách suất chiếu |
| GET | `/showtimes/{id}` | Chi tiết suất chiếu |
| POST | `/showtimes` | Tạo suất chiếu (Admin) |
| POST | `/showtimes/bulk` | Tạo nhiều suất chiếu (Admin) |
| PUT | `/showtimes/{id}` | Cập nhật suất chiếu (Admin) |
| DELETE | `/showtimes/{id}` | Xóa suất chiếu (Admin) |
| PATCH | `/showtimes/{id}/activate` | Kích hoạt (Admin) |
| PATCH | `/showtimes/{id}/deactivate` | Vô hiệu hoá (Admin) |

### Payments (`/payments`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/vnpay/create` | Tạo giao dịch VNPay |
| GET | `/payments/vnpay/ipn` | VNPay IPN Webhook |
| GET | `/payments/vnpay/verify-return` | Verify VNPay Return URL |

## Database Schema

**Models chính:**

- **Users** — UUID PK, email, username, role (user/admin), argon2 hashed password
- **Movies** — title, duration, release/end dates, director, cast, genres (M2M)
- **Genres** — name, slug, linked to movies
- **Cinemas** — name, address, city, lat/lng, rooms
- **Rooms** — cinema_id, name, type (2D/3D), row/seat layout
- **Seats** — room_id, row_label, seat_number, type (standard/vip/couple/sweetbox), price multiplier
- **Showtimes** — movie_id, room_id, start/end time, base_price
- **Bookings** — user_id, showtime_id, booking_code, status workflow (pending → confirmed/cancelled/expired)
- **BookingSeats** — booking_id, seat_id, price
- **Payments** — booking_id, VNPay transaction, status (pending/completed/failed/refunded), JSONB callback data

## Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL 16+**
- **Redis 7+**
- **Node.js 20+** (cho frontend)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/CongBinh99999/movie-booking.git
cd movie-booking

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình environment
cp .env.example .env
# Chỉnh sửa .env với database credentials của bạn

# Chạy server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy dev server
npm run dev
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT signing key | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `VNPAY_TMN_CODE` | VNPay merchant code | — |
| `VNPAY_HASH_SECRET` | VNPay hash secret | — |
| `SEAT_LOCK_TTL` | Seat lock timeout (seconds) | `900` |

## Architecture

```
Client → Next.js (Frontend)
              ↓
         FastAPI (Backend)
              ↓
    Router → Service → Repository → Database (PostgreSQL)
                ↓
              Redis (Seat locking / Caching)
                ↓
              VNPay (Payment Gateway)
```

**Patterns:**

- **Service-Repository** — Business logic tách biệt khỏi data access
- **Dependency Injection** — FastAPI `Depends()` + `Annotated` types
- **Domain-driven schemas** — API schemas (request/response) tách biệt domain schemas (DTO)
- **Async-first** — Toàn bộ I/O operations là async (`asyncpg`, `redis.asyncio`)

## License

MIT
