"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useShowtime, useAvailableSeats } from "@/hooks/useShowtimes";
import { useCreateBooking } from "@/hooks/useBookings";
import { useAuthStore } from "@/store/auth.store";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { Loader2, Info } from "lucide-react";
import type { Seat } from "@/types";

const SEAT_TYPE_STYLES: Record<Seat["seat_type"], string> = {
    standard: "bg-white/10 hover:bg-blue-500/40 border-white/20",
    vip: "bg-yellow-900/20 hover:bg-yellow-500/40 border-yellow-500/30",
    couple: "bg-pink-900/20 hover:bg-pink-500/40 border-pink-500/30",
};

const SEAT_TYPE_LABELS: Record<Seat["seat_type"], string> = {
    standard: "Thường",
    vip: "VIP",
    couple: "Couple",
};

export default function BookingPage() {
    const { showtimeId } = useParams<{ showtimeId: string }>();
    const router = useRouter();
    const { isAuthenticated } = useAuthStore();
    const [selectedSeatIds, setSelectedSeatIds] = useState<string[]>([]);
    const [errorMessage, setErrorMessage] = useState("");

    const { data: showtime, isLoading: isLoadingShowtime } = useShowtime(showtimeId);
    const { data: seats, isLoading: isLoadingSeats } = useAvailableSeats(showtimeId);
    const createBooking = useCreateBooking();

    const toggleSeat = (seatId: string) => {
        setSelectedSeatIds((prev) =>
            prev.includes(seatId) ? prev.filter((id) => id !== seatId) : [...prev, seatId]
        );
    };

    const selectedSeats = seats?.filter((s) => selectedSeatIds.includes(s.id)) ?? [];
    const totalPrice = selectedSeats.reduce((sum, seat) => sum + seat.price, 0);

    const handleConfirmBooking = async () => {
        if (!isAuthenticated) {
            router.push("/login");
            return;
        }
        if (selectedSeatIds.length === 0) {
            setErrorMessage("Vui lòng chọn ít nhất một ghế.");
            return;
        }
        setErrorMessage("");
        try {
            const booking = await createBooking.mutateAsync({
                showtime_id: showtimeId,
                seat_ids: selectedSeatIds,
            });
            router.push(`/payment/${booking.id}`);
        } catch {
            setErrorMessage("Không thể đặt vé. Ghế có thể đã được người khác đặt. Vui lòng thử lại.");
        }
    };

    // Group seats by row
    const seatsByRow = (seats ?? []).reduce<Record<string, Seat[]>>((acc, seat) => {
        if (!acc[seat.row]) acc[seat.row] = [];
        acc[seat.row].push(seat);
        return acc;
    }, {});

    if (isLoadingShowtime || isLoadingSeats) {
        return (
            <div className="pt-24 flex items-center justify-center min-h-screen">
                <Loader2 className="w-8 h-8 animate-spin text-[#e50914]" />
            </div>
        );
    }

    return (
        <div className="pt-20 pb-12 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 animate-fade-in">
            <h1 className="text-2xl font-bold text-white mb-2">Chọn ghế</h1>
            {showtime && (
                <p className="text-sm text-[#8888aa] mb-8">
                    {showtime.movie?.title} &bull; {formatDate(showtime.start_time)} &bull;{" "}
                    {formatTime(showtime.start_time)} - {formatTime(showtime.end_time)}
                </p>
            )}

            {/* Screen indicator */}
            <div className="mb-8 text-center">
                <div className="inline-block w-2/3 h-2 bg-gradient-to-r from-transparent via-[#e50914]/50 to-transparent rounded-full mb-2" />
                <p className="text-xs text-[#8888aa] uppercase tracking-widest">Màn hình</p>
            </div>

            {/* Seat map */}
            <div className="glass-card rounded-2xl p-6 mb-6 overflow-x-auto">
                {Object.entries(seatsByRow)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([row, rowSeats]) => (
                        <div key={row} className="flex items-center gap-2 mb-2">
                            <span className="text-xs text-[#8888aa] w-5 text-center font-semibold">{row}</span>
                            <div className="flex gap-1.5 flex-wrap">
                                {rowSeats
                                    .sort((a, b) => a.column - b.column)
                                    .map((seat) => {
                                        const isSelected = selectedSeatIds.includes(seat.id);
                                        return (
                                            <button
                                                key={seat.id}
                                                onClick={() => toggleSeat(seat.id)}
                                                title={`${seat.seat_type} - ${formatCurrency(seat.price)}`}
                                                className={cn(
                                                    "w-9 h-9 text-xs font-semibold rounded-lg border transition-all duration-150 cursor-pointer",
                                                    isSelected
                                                        ? "bg-[#e50914] border-[#e50914] text-white scale-110"
                                                        : SEAT_TYPE_STYLES[seat.seat_type]
                                                )}
                                            >
                                                {seat.column}
                                            </button>
                                        );
                                    })}
                            </div>
                        </div>
                    ))}
                {Object.keys(seatsByRow).length === 0 && (
                    <p className="text-center text-[#8888aa] my-8">Không còn ghế trống</p>
                )}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-4 justify-center mb-8">
                {(["standard", "vip", "couple"] as Seat["seat_type"][]).map((type) => (
                    <div key={type} className="flex items-center gap-2">
                        <div className={cn("w-6 h-6 rounded border", SEAT_TYPE_STYLES[type])} />
                        <span className="text-xs text-[#8888aa]">{SEAT_TYPE_LABELS[type]}</span>
                    </div>
                ))}
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded bg-[#e50914] border border-[#e50914]" />
                    <span className="text-xs text-[#8888aa]">Đang chọn</span>
                </div>
            </div>

            {/* Order summary */}
            <div className="glass-card rounded-2xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Xác nhận đặt vé</h2>
                {selectedSeats.length > 0 ? (
                    <div className="space-y-2 mb-4">
                        {selectedSeats.map((seat) => (
                            <div key={seat.id} className="flex justify-between text-sm">
                                <span className="text-[#8888aa]">
                                    Ghế {seat.row}{seat.column} ({SEAT_TYPE_LABELS[seat.seat_type]})
                                </span>
                                <span className="text-white">{formatCurrency(seat.price)}</span>
                            </div>
                        ))}
                        <div className="border-t border-white/10 pt-2 flex justify-between font-semibold">
                            <span className="text-white">Tổng cộng</span>
                            <span className="text-[#e50914] text-lg">{formatCurrency(totalPrice)}</span>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center gap-2 text-sm text-[#8888aa] mb-4">
                        <Info className="w-4 h-4" />
                        Chưa chọn ghế nào
                    </div>
                )}

                {errorMessage && (
                    <p className="text-red-400 text-sm mb-3">{errorMessage}</p>
                )}

                <button
                    onClick={handleConfirmBooking}
                    disabled={createBooking.isPending || selectedSeatIds.length === 0}
                    className="w-full flex items-center justify-center gap-2 py-3.5 bg-[#e50914] hover:bg-[#b20710] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors duration-200 cursor-pointer"
                >
                    {createBooking.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                    {isAuthenticated ? "Tiến hành thanh toán" : "Đăng nhập để đặt vé"}
                </button>
            </div>
        </div>
    );
}
