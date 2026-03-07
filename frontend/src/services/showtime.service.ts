import { apiClient } from "@/lib/api";
import type { Showtime, Seat } from "@/types";

export const showtimeService = {
    getShowtimesByMovie: async (movieId: string): Promise<Showtime[]> => {
        const response = await apiClient.get<Showtime[]>(`/showtimes`, {
            params: { movie_id: movieId },
        });
        return response.data;
    },

    getShowtimeById: async (id: string): Promise<Showtime> => {
        const response = await apiClient.get<Showtime>(`/showtimes/${id}`);
        return response.data;
    },

    getAvailableSeats: async (showtimeId: string): Promise<Seat[]> => {
        const response = await apiClient.get<Seat[]>(`/showtimes/${showtimeId}/seats`);
        return response.data;
    },
};
