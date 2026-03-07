import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { movieService, type MovieFilters } from "@/services/movie.service";

export function useMovies(filters?: MovieFilters) {
    return useQuery({
        queryKey: ["movies", filters],
        queryFn: () => movieService.getMovies(filters),
    });
}

export function useMovie(id: string) {
    return useQuery({
        queryKey: ["movie", id],
        queryFn: () => movieService.getMovieById(id),
        enabled: !!id,
    });
}

export function useGenres() {
    return useQuery({
        queryKey: ["genres"],
        queryFn: () => movieService.getGenres(),
        staleTime: 1000 * 60 * 60, // 1 hour
    });
}

export function useNowShowing() {
    return useQuery({
        queryKey: ["movies", "now-showing"],
        queryFn: () => movieService.getNowShowing(),
    });
}

export function useComingSoon() {
    return useQuery({
        queryKey: ["movies", "coming-soon"],
        queryFn: () => movieService.getComingSoon(),
    });
}
