import { apiClient } from "@/lib/api";
import type { Booking, CreateBookingData, PaginatedResponse } from "@/types";

export const bookingService = {
    createBooking: async (data: CreateBookingData): Promise<Booking> => {
        const response = await apiClient.post<Booking>("/bookings", data);
        return response.data;
    },

    getMyBookings: async (page = 1, size = 20): Promise<PaginatedResponse<Booking>> => {
        const response = await apiClient.get<PaginatedResponse<Booking>>("/bookings", { params: { page, size } });
        return response.data;
    },

    getBookingById: async (id: string): Promise<Booking> => {
        const response = await apiClient.get<Booking>(`/bookings/${id}`);
        return response.data;
    },

    cancelBooking: async (id: string, reason?: string): Promise<Booking> => {
        const response = await apiClient.post<Booking>(`/bookings/${id}/cancel`, reason ? { cancellation_reason: reason } : undefined);
        return response.data;
    },
};
