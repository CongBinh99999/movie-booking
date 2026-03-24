"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Ticket, Calendar, Loader2, AlertCircle } from "lucide-react";
import { useMyBookings } from "@/hooks/useBookings";
import { useAuthStore } from "@/store/auth.store";
import { formatCurrency } from "@/lib/utils";
import type { BookingStatus } from "@/types";

const STATUS_CONFIG: Record<BookingStatus, { label: string; color: string }> = {
    pending: { label: "Chờ thanh toán", color: "bg-yellow-500/15 text-yellow-400" },
    confirmed: { label: "Đã xác nhận", color: "bg-green-500/15 text-green-400" },
    cancelled: { label: "Đã hủy", color: "bg-red-500/15 text-red-400" },
    expired: { label: "Hết hạn", color: "bg-gray-500/15 text-gray-400" },
};

export default function BookingsPage() {
    const router = useRouter();
    const { isAuthenticated, user } = useAuthStore();
    const { data, isLoading, error } = useMyBookings();

    useEffect(() => {
        if (!isAuthenticated || !user) {
            router.push("/login");
        }
    }, [isAuthenticated, user, router]);

    if (!isAuthenticated || !user) {
        return null;
    }

    return (
        <div className="pt-16 pb-12 min-h-screen">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
                {/* Header */}
                <div className="flex items-center gap-3 mb-8">
                    <div className="p-2.5 bg-[#e50914]/10 rounded-xl">
                        <Ticket className="w-6 h-6 text-[#e50914]" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Vé của tôi</h1>
                        <p className="text-[#8888aa] text-sm">Quản lý các đơn đặt vé của bạn</p>
                    </div>
                </div>

                {/* Loading */}
                {isLoading && (
                    <div className="flex flex-col items-center justify-center py-20">
                        <Loader2 className="w-8 h-8 text-[#e50914] animate-spin mb-3" />
                        <p className="text-[#8888aa] text-sm">Đang tải danh sách vé...</p>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="glass-card rounded-2xl p-6 flex items-center gap-3 text-red-400">
                        <AlertCircle className="w-5 h-5 shrink-0" />
                        <p className="text-sm">Có lỗi xảy ra khi tải danh sách vé. Vui lòng thử lại.</p>
                    </div>
                )}

                {/* Empty state */}
                {!isLoading && !error && data?.items?.length === 0 && (
                    <div className="glass-card rounded-2xl p-12 text-center">
                        <Ticket className="w-12 h-12 text-[#8888aa] mx-auto mb-4 opacity-50" />
                        <h3 className="text-lg font-semibold text-white mb-2">Chưa có vé nào</h3>
                        <p className="text-[#8888aa] text-sm mb-6">Hãy đặt vé xem phim đầu tiên của bạn!</p>
                        <Link
                            href="/movies"
                            className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#e50914] hover:bg-[#b20710] text-white text-sm font-medium rounded-xl transition-colors"
                        >
                            Xem phim
                        </Link>
                    </div>
                )}

                {/* Booking list */}
                {!isLoading && data?.items && data.items.length > 0 && (
                    <div className="space-y-3">
                        {data.items.map((booking) => {
                            const statusConfig = STATUS_CONFIG[booking.status] ?? { label: booking.status, color: "bg-gray-500/15 text-gray-400" };

                            return (
                                <Link
                                    key={booking.id}
                                    href={`/bookings/${booking.id}`}
                                    className="block glass-card rounded-2xl p-5 hover:bg-white/5 hover:border-white/15 transition-all duration-200 group cursor-pointer"
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className="text-white font-semibold text-sm">
                                                    #{booking.booking_code}
                                                </span>
                                                <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${statusConfig.color}`}>
                                                    {statusConfig.label}
                                                </span>
                                            </div>
                                            {booking.created_at && (
                                                <div className="flex items-center gap-1.5 text-[#8888aa] text-xs">
                                                    <Calendar className="w-3.5 h-3.5" />
                                                    <span>{new Date(booking.created_at).toLocaleString("vi-VN")}</span>
                                                </div>
                                            )}
                                        </div>
                                        <div className="text-right">
                                            <div className="text-[#e50914] font-bold text-sm">
                                                {formatCurrency(booking.total_amount)}
                                            </div>
                                        </div>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                )}

                {/* Pagination info */}
                {data && data.total > 0 && (
                    <div className="mt-6 text-center text-[#8888aa] text-xs">
                        Hiển thị {data.items.length} / {data.total} đơn đặt vé
                    </div>
                )}
            </div>
        </div>
    );
}
