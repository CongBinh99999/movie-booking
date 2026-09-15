import { apiClient } from "@/lib/api";
import type { PaginatedResponse, SeatAvailability, Showtime } from "@/types";

export const showtimeService = {
    /** /showtimes trả ShowtimeListResponse có phân trang. */
    getShowtimesByMovie: async (movieId: string): Promise<Showtime[]> => {
        const response = await apiClient.get<PaginatedResponse<Showtime>>("/showtimes", {
            params: { movie_id: movieId, is_active: true, size: 100 },
        });
        return response.data.items;
    },

    getShowtimeById: async (id: string): Promise<Showtime> => {
        const response = await apiClient.get<Showtime>(`/showtimes/${id}`);
        return response.data;
    },

    /**
     * Trả cả object chứ không chỉ mảng ghế: base_price và available_count
     * được tính sẵn ở backend, dùng luôn thay vì tính lại ở client.
     */
    getAvailableSeats: async (showtimeId: string): Promise<SeatAvailability> => {
        const response = await apiClient.get<SeatAvailability>(
            `/showtimes/${showtimeId}/seats`
        );
        return response.data;
    },
};
