"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AlertCircle, CreditCard, Loader2, Ticket } from "lucide-react";
import { useBooking } from "@/hooks/useBookings";
import { useCreateVNPayPayment } from "@/hooks/usePayment";
import { useAuthStore } from "@/store/auth.store";
import { formatCurrency } from "@/lib/utils";

export default function PaymentPage({ params }: { params: Promise<{ bookingId: string }> }) {
    const { bookingId } = use(params);
    const router = useRouter();
    const { isAuthenticated } = useAuthStore();
    const { data: booking, isLoading, error } = useBooking(bookingId);
    const createPayment = useCreateVNPayPayment();
    const [errorMessage, setErrorMessage] = useState("");

    useEffect(() => {
        if (!isAuthenticated) router.push("/login");
    }, [isAuthenticated, router]);

    const handlePay = async () => {
        setErrorMessage("");
        try {
            const { payment_url } = await createPayment.mutateAsync(bookingId);
            // Rời khỏi app sang cổng VNPay.
            window.location.href = payment_url;
        } catch {
            setErrorMessage(
                "Không tạo được giao dịch. Đơn có thể đã hết hạn hoặc đã được xử lý."
            );
        }
    };

    if (!isAuthenticated) return null;

    return (
        <div className="pt-16 pb-12 min-h-screen">
            <div className="max-w-lg mx-auto px-4 sm:px-6 py-8 animate-fade-in">
                <div className="flex items-center gap-3 mb-8">
                    <div className="p-2.5 bg-[#e50914]/10 rounded-xl">
                        <CreditCard className="w-6 h-6 text-[#e50914]" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Thanh toán</h1>
                        <p className="text-[#8888aa] text-sm">Hoàn tất đơn đặt vé của bạn</p>
                    </div>
                </div>

                {isLoading && (
                    <div className="flex flex-col items-center justify-center py-20">
                        <Loader2 className="w-8 h-8 text-[#e50914] animate-spin mb-3" />
                        <p className="text-[#8888aa] text-sm">Đang tải đơn đặt vé...</p>
                    </div>
                )}

                {error && (
                    <div className="glass-card rounded-2xl p-6 flex items-center gap-3 text-red-400">
                        <AlertCircle className="w-5 h-5 shrink-0" />
                        <p className="text-sm">Không tìm thấy đơn đặt vé này.</p>
                    </div>
                )}

                {booking && (
                    <div className="glass-card rounded-2xl p-6 space-y-5">
                        <div className="flex items-center gap-2 text-[#8888aa] text-sm">
                            <Ticket className="w-4 h-4" />
                            <span>Mã đơn</span>
                            <span className="text-white font-medium ml-auto">
                                {booking.booking_code}
                            </span>
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-white/10">
                            <span className="text-[#8888aa] text-sm">Tổng tiền</span>
                            <span className="text-[#e50914] text-xl font-semibold">
                                {formatCurrency(booking.total_amount)}
                            </span>
                        </div>

                        {booking.status !== "pending" ? (
                            <div className="text-sm text-[#8888aa]">
                                Đơn này không ở trạng thái chờ thanh toán.{" "}
                                <Link href="/bookings" className="text-[#e50914] hover:underline">
                                    Xem vé của tôi
                                </Link>
                            </div>
                        ) : (
                            <button
                                onClick={handlePay}
                                disabled={createPayment.isPending}
                                className="w-full py-3 rounded-xl bg-[#e50914] text-white font-medium
                                           hover:bg-[#c40812] disabled:opacity-60 transition-colors"
                            >
                                {createPayment.isPending ? "Đang chuyển hướng..." : "Thanh toán qua VNPay"}
                            </button>
                        )}

                        {errorMessage && (
                            <p className="text-red-400 text-sm flex items-center gap-2">
                                <AlertCircle className="w-4 h-4 shrink-0" />
                                {errorMessage}
                            </p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
