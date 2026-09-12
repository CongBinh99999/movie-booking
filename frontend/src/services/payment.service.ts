import { apiClient } from "@/lib/api";

export interface VNPayPaymentResponse {
    payment_url: string;
}

export interface VNPayReturnResult {
    is_valid: boolean;
    is_success: boolean;
}

export const paymentService = {
    /** POST /payments/vnpay/create — backend nhận booking_id qua query string. */
    createVNPayPayment: async (bookingId: string): Promise<VNPayPaymentResponse> => {
        const response = await apiClient.post<VNPayPaymentResponse>(
            "/payments/vnpay/create",
            null,
            { params: { booking_id: bookingId } }
        );
        return response.data;
    },

    /** GET /payments/vnpay/verify-return — chỉ xác thực chữ ký để render UI. */
    verifyVNPayReturn: async (params: URLSearchParams): Promise<VNPayReturnResult> => {
        const response = await apiClient.get<VNPayReturnResult>(
            "/payments/vnpay/verify-return",
            { params: Object.fromEntries(params) }
        );
        return response.data;
    },
};
