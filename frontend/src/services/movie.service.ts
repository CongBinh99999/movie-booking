import { apiClient } from "@/lib/api";
import type { Movie, Genre, PaginatedResponse } from "@/types";

export interface MovieFilters {
    page?: number;
    size?: number;
    status?: "coming_soon" | "now_showing" | "ended";
    genre_id?: string;
    search?: string;
}

export const movieService = {
    getMovies: async (filters?: MovieFilters): Promise<PaginatedResponse<Movie>> => {
        const response = await apiClient.get<PaginatedResponse<Movie>>("/movies", {
            params: filters,
        });
        return response.data;
    },

    getMovieById: async (id: string): Promise<Movie> => {
        const response = await apiClient.get<Movie>(`/movies/${id}`);
        return response.data;
    },

    getGenres: async (): Promise<Genre[]> => {
        const response = await apiClient.get<Genre[]>("/genres");
        return response.data;
    },

    getNowShowing: async (): Promise<PaginatedResponse<Movie>> => {
        return movieService.getMovies({ status: "now_showing", size: 10 });
    },

    getComingSoon: async (): Promise<PaginatedResponse<Movie>> => {
        return movieService.getMovies({ status: "coming_soon", size: 10 });
    },
};
