import { apiClient } from "@/lib/api";
import type { Genre, Movie, PaginatedResponse } from "@/types";

/** Backend nhận skip/limit, không phải page/size (xem MovieQueryParams). */
export interface MovieFilters {
    skip?: number;
    limit?: number;
    status?: "coming_soon" | "now_showing" | "ended";
    title?: string;
    is_active?: boolean;
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

    /** /genres trả GenreListResponse có phân trang; ở đây chỉ cần danh sách. */
    getGenres: async (): Promise<Genre[]> => {
        const response = await apiClient.get<PaginatedResponse<Genre>>("/genres", {
            params: { limit: 100 },
        });
        return response.data.items;
    },

    getNowShowing: async (limit = 12): Promise<PaginatedResponse<Movie>> =>
        movieService.getMovies({ status: "now_showing", limit }),

    getComingSoon: async (limit = 12): Promise<PaginatedResponse<Movie>> =>
        movieService.getMovies({ status: "coming_soon", limit }),
};
