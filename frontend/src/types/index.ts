// Auth types
export interface User {
    id: string;
    email: string;
    full_name: string;
    phone_number?: string;
    role: "admin" | "customer";
    is_active: boolean;
    created_at: string;
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
    token_type: string;
}

// Movie types
export interface Genre {
    id: string;
    name: string;
}

export interface Movie {
    id: string;
    title: string;
    description: string;
    duration: number; // minutes
    release_date: string;
    poster_url?: string;
    trailer_url?: string;
    rating?: number;
    genres: Genre[];
    status: "coming_soon" | "now_showing" | "ended";
}

// Cinema types
export interface Cinema {
    id: string;
    name: string;
    address: string;
    city: string;
    phone_number?: string;
}

export interface Room {
    id: string;
    name: string;
    cinema_id: string;
    total_seats: number;
}

export interface Seat {
    id: string;
    room_id: string;
    row: string;
    column: number;
    seat_type: "standard" | "vip" | "couple";
    price: number;
}

// Showtime types
export interface Showtime {
    id: string;
    movie_id: string;
    room_id: string;
    start_time: string;
    end_time: string;
    price: number;
    movie?: Movie;
    room?: Room;
}

// Booking types
export type BookingStatus = "pending" | "confirmed" | "cancelled" | "expired";

export interface BookingSeat {
    id: string;
    seat_id: string;
    seat?: Seat;
}

export interface Booking {
    id: string;
    user_id?: string;
    showtime_id?: string;
    booking_code: string;
    status: BookingStatus;
    total_amount: number;
    created_at?: string;
    expires_at?: string;
    confirmed_at?: string;
    cancelled_at?: string;
    cancellation_reason?: string;
    showtime?: Showtime;
    seats?: BookingSeat[];
}

export interface CreateBookingData {
    showtime_id: string;
    seat_ids: string[];
}

// Payment types
export type PaymentStatus = "pending" | "completed" | "failed" | "refunded";
export type PaymentMethod = "vnpay" | "credit_card" | "cash";

export interface Payment {
    id: string;
    booking_id: string;
    amount: number;
    status: PaymentStatus;
    method: PaymentMethod;
    transaction_id?: string;
    created_at: string;
}

// Paginated response
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
}

// Error response from API
export interface ApiError {
    error_code: string;
    message: string;
    details?: Record<string, unknown>;
}
