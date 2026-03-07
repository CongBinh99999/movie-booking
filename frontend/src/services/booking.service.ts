import { apiClient } from "@/lib/api";
import type { Booking, CreateBookingData, PaginatedResponse } from "@/types";

export const bookingService = {
    createBooking: async (data: CreateBookingData): Promise<Booking> => {
        const response = await apiClient.post<Booking>("/bookings", data);
        return response.data;
    },

    getMyBookings: async (): Promise<PaginatedResponse<Booking>> => {
        const response = await apiClient.get<PaginatedResponse<Booking>>("/bookings/me");
        return response.data;
    },

    getBookingById: async (id: string): Promise<Booking> => {
        const response = await apiClient.get<Booking>(`/bookings/${id}`);
        return response.data;
    },

    cancelBooking: async (id: string): Promise<Booking> => {
        const response = await apiClient.patch<Booking>(`/bookings/${id}/cancel`);
        return response.data;
    },

    confirmBooking: async (id: string): Promise<Booking> => {
        const response = await apiClient.patch<Booking>(`/bookings/${id}/confirm`);
        return response.data;
    },
};
