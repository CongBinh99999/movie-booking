import { apiClient } from "@/lib/api";
import type { Payment } from "@/types";

export interface CreatePaymentData {
    booking_id: string;
    method: "vnpay" | "credit_card" | "cash";
    return_url?: string;
}

export interface VNPayPaymentResponse {
    payment_url: string;
}

export const paymentService = {
    createPayment: async (
        data: CreatePaymentData
    ): Promise<Payment | VNPayPaymentResponse> => {
        const response = await apiClient.post<Payment | VNPayPaymentResponse>(
            "/payments",
            data
        );
        return response.data;
    },

    getPaymentByBookingId: async (bookingId: string): Promise<Payment> => {
        const response = await apiClient.get<Payment>(`/payments/booking/${bookingId}`);
        return response.data;
    },

    verifyVNPayCallback: async (params: URLSearchParams): Promise<Payment> => {
        const response = await apiClient.get<Payment>(`/payments/vnpay/callback`, {
            params: Object.fromEntries(params),
        });
        return response.data;
    },
};
