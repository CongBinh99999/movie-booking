/**
 * Kiểu dữ liệu API — đối chiếu với OpenAPI của backend.
 *
 * Lưu ý về tiền: backend dùng Decimal, FastAPI serialize thành **chuỗi**
 * ("260000.00"), không phải số. Dùng `toNumber()` trước khi tính toán —
 * cộng thẳng hai chuỗi sẽ ra nối chuỗi chứ không ra tổng.
 */

/** Decimal của backend, luôn về dưới dạng chuỗi. */
export type Decimal = string;

export function toNumber(value: Decimal | number | null | undefined): number {
    return typeof value === "number" ? value : Number(value ?? 0);
}

// ── Auth ─────────────────────────────────────────────────────────────
// Khớp UserResponse (app/modules/auth/schemas/api.py).
export type UserRole = "user" | "admin";

export interface User {
    id: string;
    email: string;
    username: string;
    full_name: string | null;
    role: UserRole;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface RegisterData {
    email: string;
    username: string;
    password: string;
    confirmed_password: string;
    full_name?: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type?: string;
    expires_at?: string | null;
}

// ── Movies ───────────────────────────────────────────────────────────
// Khớp GenreResponse.
export interface Genre {
    id: string;
    name: string;
    slug: string;
    created_at: string;
}

/**
 * Khớp MovieResponse. Không có trường `status` — trạng thái chiếu suy ra từ
 * `is_active` + `release_date` + `end_date` (xem `getMovieStatus`).
 * Cũng không kèm `genres`; danh sách thể loại lấy từ endpoint riêng.
 */
export interface Movie {
    id: string;
    title: string;
    original_title: string;
    description: string | null;
    duration_minutes: number;
    release_date: string | null;
    end_date: string | null;
    poster_url: string | null;
    trailer_url: string | null;
    director: string | null;
    cast_members: string[];
    language: string | null;
    subtitle: string | null;
    age_rating: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export type MovieStatus = "now_showing" | "coming_soon" | "ended";

export function getMovieStatus(movie: Movie, now: Date = new Date()): MovieStatus {
    if (!movie.release_date) return "coming_soon";
    const today = now.toISOString().slice(0, 10);
    if (movie.release_date > today) return "coming_soon";
    if (movie.end_date && movie.end_date < today) return "ended";
    return "now_showing";
}

/** Khớp MovieBasic — bản rút gọn nhúng trong ShowtimeResponse. */
export interface MovieBasic {
    id: string;
    title: string;
    poster_url: string | null;
    duration_minutes: number;
}

// ── Cinemas / rooms / seats ──────────────────────────────────────────
export interface CinemaBasic {
    id: string;
    name: string;
    city: string;
}

export interface RoomBasic {
    id: string;
    name: string;
    room_type: string;
}

export type SeatType = "standard" | "vip" | "couple" | "sweetbox";
export type SeatStatus = "available" | "booked" | "locked";

/** Khớp SeatAvailabilityInfo — ghế kèm trạng thái cho một suất chiếu. */
export interface Seat {
    id: string;
    row_label: string;
    seat_number: number;
    seat_type: SeatType;
    base_price: Decimal;
    price_multiplier: Decimal;
    final_price: Decimal;
    status?: SeatStatus;
}

/** Khớp SeatAvailabilityResponse. */
export interface SeatAvailability {
    showtime_id: string;
    base_price: Decimal;
    seats: Seat[];
    total_seats: number;
    available_count: number;
}

export function seatLabel(seat: Pick<Seat, "row_label" | "seat_number">): string {
    return `${seat.row_label}${seat.seat_number}`;
}

// ── Showtimes ────────────────────────────────────────────────────────
// Khớp ShowtimeResponse.
export interface Showtime {
    id: string;
    movie_id: string;
    room_id: string;
    start_time: string;
    end_time: string;
    base_price: Decimal;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    movie?: MovieBasic | null;
    room?: RoomBasic | null;
    cinema?: CinemaBasic | null;
}

// ── Bookings ─────────────────────────────────────────────────────────
export type BookingStatus = "pending" | "confirmed" | "cancelled" | "expired";

/** Khớp BookingDTO. */
export interface Booking {
    id: string;
    user_id: string;
    showtime_id: string;
    booking_code: string;
    status: BookingStatus;
    total_amount: Decimal;
    expires_at: string;
    confirmed_at?: string | null;
    cancelled_at?: string | null;
    cancellation_reason?: string | null;
    created_at: string;
    updated_at: string;
}

export interface CreateBookingData {
    showtime_id: string;
    seat_ids: string[];
}

// ── Payments ─────────────────────────────────────────────────────────
export type PaymentStatus = "pending" | "completed" | "failed" | "refunded";

// ── Chung ────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages?: number;
    has_next?: boolean;
    has_prev?: boolean;
}

/** Thân lỗi do app_exception_handler của backend trả về. */
export interface ApiError {
    error_code: string;
    message: string;
    details?: Record<string, unknown>;
}
