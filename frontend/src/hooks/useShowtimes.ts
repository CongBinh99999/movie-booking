import { useQuery } from "@tanstack/react-query";
import { showtimeService } from "@/services/showtime.service";

export function useShowtimesByMovie(movieId: string) {
    return useQuery({
        queryKey: ["showtimes", "movie", movieId],
        queryFn: () => showtimeService.getShowtimesByMovie(movieId),
        enabled: !!movieId,
    });
}

export function useShowtime(id: string) {
    return useQuery({
        queryKey: ["showtime", id],
        queryFn: () => showtimeService.getShowtimeById(id),
        enabled: !!id,
    });
}

export function useAvailableSeats(showtimeId: string) {
    return useQuery({
        queryKey: ["seats", showtimeId],
        queryFn: () => showtimeService.getAvailableSeats(showtimeId),
        enabled: !!showtimeId,
        refetchInterval: 5000, // Poll every 5s for real-time seat availability
    });
}
