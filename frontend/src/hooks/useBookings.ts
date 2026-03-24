import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { bookingService } from "@/services/booking.service";
import type { CreateBookingData } from "@/types";

export function useMyBookings() {
    return useQuery({
        queryKey: ["bookings", "me"],
        queryFn: () => bookingService.getMyBookings(),
    });
}

export function useBooking(id: string) {
    return useQuery({
        queryKey: ["booking", id],
        queryFn: () => bookingService.getBookingById(id),
        enabled: !!id,
    });
}

export function useCreateBooking() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: CreateBookingData) => bookingService.createBooking(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bookings"] });
        },
    });
}

export function useCancelBooking() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => bookingService.cancelBooking(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bookings"] });
        },
    });
}
