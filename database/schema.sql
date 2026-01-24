-- ============================================
-- Movie Booking System - Database Schema
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUM TYPES
-- ============================================

CREATE TYPE user_role AS ENUM ('user', 'admin');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'cancelled', 'expired');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');
CREATE TYPE payment_method AS ENUM ('vnpay', 'momo', 'zalopay');
CREATE TYPE seat_type AS ENUM ('standard', 'vip', 'couple', 'sweetbox');

-- ============================================
-- MODULE: AUTH
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- MODULE: MOVIES
-- ============================================

CREATE TABLE genres (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE movies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    original_title VARCHAR(255),
    description TEXT,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0 AND duration_minutes <= 500),
    release_date DATE,
    end_date DATE,
    poster_url VARCHAR(500),
    trailer_url VARCHAR(500),
    director VARCHAR(255),
    cast_members TEXT[], -- Array of actor names
    language VARCHAR(50),
    subtitle VARCHAR(50),
    age_rating VARCHAR(10), -- P, C13, C16, C18
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_is_active ON movies(is_active);

-- Movie-Genre many-to-many relationship
CREATE TABLE movie_genres (
    movie_id UUID NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    genre_id UUID NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

CREATE INDEX idx_movie_genres_movie_id ON movie_genres(movie_id);
CREATE INDEX idx_movie_genres_genre_id ON movie_genres(genre_id);

-- ============================================
-- MODULE: CINEMAS
-- ============================================

CREATE TABLE cinemas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    description TEXT,
    image_url VARCHAR(500),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cinemas_city ON cinemas(city);
CREATE INDEX idx_cinemas_is_active ON cinemas(is_active);

CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cinema_id UUID NOT NULL REFERENCES cinemas(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    room_type VARCHAR(50) NOT NULL DEFAULT '2D', -- 2D, 3D, IMAX, 4DX
    total_rows INTEGER NOT NULL CHECK (total_rows > 0),
    seats_per_row INTEGER NOT NULL CHECK (seats_per_row > 0),
    total_seats INTEGER NOT NULL CHECK (total_seats > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cinema_id, name)
);

CREATE INDEX idx_rooms_cinema_id ON rooms(cinema_id);
CREATE INDEX idx_rooms_is_active ON rooms(is_active);

CREATE TABLE seats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    row_label CHAR(1) NOT NULL, -- A, B, C, ...
    seat_number INTEGER NOT NULL CHECK (seat_number > 0),
    seat_type seat_type NOT NULL DEFAULT 'standard',
    price_multiplier DECIMAL(3, 2) NOT NULL DEFAULT 1.00, -- 1.0 = standard, 1.5 = VIP
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(room_id, row_label, seat_number)
);

CREATE INDEX idx_seats_room_id ON seats(room_id);
CREATE INDEX idx_seats_seat_type ON seats(seat_type);

-- ============================================
-- MODULE: SHOWTIMES
-- ============================================

CREATE TABLE showtimes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    movie_id UUID NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    base_price DECIMAL(12, 2) NOT NULL CHECK (base_price > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_time_range CHECK (end_time > start_time)
);

CREATE INDEX idx_showtimes_movie_id ON showtimes(movie_id);
CREATE INDEX idx_showtimes_room_id ON showtimes(room_id);
CREATE INDEX idx_showtimes_start_time ON showtimes(start_time);
CREATE INDEX idx_showtimes_is_active ON showtimes(is_active);

-- Composite index for overlap checking
CREATE INDEX idx_showtimes_room_time ON showtimes(room_id, start_time, end_time);

-- ============================================
-- MODULE: BOOKINGS
-- ============================================

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    showtime_id UUID NOT NULL REFERENCES showtimes(id) ON DELETE CASCADE,
    booking_code VARCHAR(20) NOT NULL UNIQUE, -- E.g., MB20261001ABC
    status booking_status NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL, -- 15 minutes from creation
    confirmed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_showtime_id ON bookings(showtime_id);
CREATE INDEX idx_bookings_booking_code ON bookings(booking_code);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_expires_at ON bookings(expires_at);

-- For finding expired pending bookings
CREATE INDEX idx_bookings_pending_expires ON bookings(status, expires_at) 
    WHERE status = 'pending';

-- Booking seats (many-to-many)
CREATE TABLE booking_seats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    seat_id UUID NOT NULL REFERENCES seats(id) ON DELETE CASCADE,
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(booking_id, seat_id)
);

CREATE INDEX idx_booking_seats_booking_id ON booking_seats(booking_id);
CREATE INDEX idx_booking_seats_seat_id ON booking_seats(seat_id);

-- Prevent double booking for the same showtime+seat
CREATE UNIQUE INDEX idx_unique_showtime_seat ON booking_seats(seat_id, booking_id);

-- ============================================
-- MODULE: PAYMENTS
-- ============================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    transaction_id VARCHAR(100) UNIQUE, -- From payment gateway
    payment_method payment_method NOT NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    status payment_status NOT NULL DEFAULT 'pending',
    payment_url TEXT, -- Redirect URL from gateway
    callback_data JSONB, -- Store raw callback from gateway
    paid_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_booking_id ON payments(booking_id);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_payment_method ON payments(payment_method);

-- ============================================
-- UTILITY: Updated_at trigger function
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_movies_updated_at BEFORE UPDATE ON movies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cinemas_updated_at BEFORE UPDATE ON cinemas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rooms_updated_at BEFORE UPDATE ON rooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_showtimes_updated_at BEFORE UPDATE ON showtimes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SAMPLE DATA: Genres
-- ============================================

INSERT INTO genres (name, slug) VALUES
    ('Hành động', 'hanh-dong'),
    ('Hài hước', 'hai-huoc'),
    ('Kinh dị', 'kinh-di'),
    ('Tình cảm', 'tinh-cam'),
    ('Hoạt hình', 'hoat-hinh'),
    ('Khoa học viễn tưởng', 'khoa-hoc-vien-tuong'),
    ('Phiêu lưu', 'phieu-luu'),
    ('Tâm lý', 'tam-ly'),
    ('Hình sự', 'hinh-su'),
    ('Gia đình', 'gia-dinh');
