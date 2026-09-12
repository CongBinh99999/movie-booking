import { useMutation } from "@tanstack/react-query";
import { paymentService } from "@/services/payment.service";

export function useCreateVNPayPayment() {
    return useMutation({
        mutationFn: (bookingId: string) => paymentService.createVNPayPayment(bookingId),
    });
}
