"use client";

import { AlertCircle, ArrowRight, Armchair, Clock } from "lucide-react";
import { useRouter } from "next/navigation";
import { use, useMemo, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Empty,
    EmptyDescription,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
} from "@/components/ui/empty";
import { Skeleton } from "@/components/ui/skeleton";
import { useCreateBooking } from "@/hooks/useBookings";
import { useAvailableSeats, useShowtime } from "@/hooks/useShowtimes";
import { cn, formatCurrency, formatDate, formatTime } from "@/lib/utils";
import { useAuthStore } from "@/store/auth.store";
import { seatLabel, toNumber, type Seat, type SeatType } from "@/types";

const MAX_SEATS = 10;

/**
 * Màu của từng trạng thái ghế, khai một lần và dùng cho CẢ ô ghế lẫn chú
 * thích bên dưới. Trước đây hai chỗ khai riêng nên chú thích nói một đằng, ghế
 * hiển thị một nẻo.
 *
 * Nền `warning` pha 18% trên nền sáng nhạt gần bằng `bg-muted`, khiến "đang
 * giữ" và "đã đặt" trông y hệt nhau. Giờ mỗi trạng thái khác nhau ở cả ba thứ:
 * nền, viền và màu chữ.
 */
const SEAT_STATE = {
    available: "border-border-strong bg-transparent text-foreground",
    booked: "border-transparent bg-muted text-muted-foreground/45",
    locked: "border-warning border-2 bg-warning/30 text-warning",
    selected: "border-transparent bg-primary text-primary-foreground",
} as const;

const SEAT_TYPE_LABEL: Record<SeatType, string> = {
    standard: "Thường",
    vip: "VIP",
    couple: "Đôi",
    sweetbox: "Sweetbox",
};

export default function BookingPage({
    params,
}: {
    params: Promise<{ showtimeId: string }>;
}) {
    const { showtimeId } = use(params);
    const router = useRouter();
    const { isAuthenticated } = useAuthStore();

    const { data: showtime, isLoading: loadingShowtime } = useShowtime(showtimeId);
    const { data: availability, isLoading: loadingSeats } = useAvailableSeats(showtimeId);
    const createBooking = useCreateBooking();

    const [selectedIds, setSelectedIds] = useState<string[]>([]);

    const seats = availability?.seats;

    // Xếp ghế theo hàng, mỗi hàng sắp theo số ghế.
    const rows = useMemo(() => {
        const grouped = new Map<string, Seat[]>();
        for (const seat of seats ?? []) {
            grouped.set(seat.row_label, [...(grouped.get(seat.row_label) ?? []), seat]);
        }
        return [...grouped.entries()]
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([row, items]) => ({
                row,
                seats: items.sort((a, b) => a.seat_number - b.seat_number),
            }));
    }, [seats]);

    const selectedSeats = (seats ?? []).filter((s) => selectedIds.includes(s.id));
    // final_price là chuỗi Decimal — cộng thẳng sẽ ra nối chuỗi, phải đổi sang số.
    const total = selectedSeats.reduce((sum, seat) => sum + toNumber(seat.final_price), 0);

    const toggleSeat = (seat: Seat) => {
        if (seat.status && seat.status !== "available") return;

        setSelectedIds((prev) => {
            if (prev.includes(seat.id)) return prev.filter((id) => id !== seat.id);
            if (prev.length >= MAX_SEATS) {
                toast.warning(`Chỉ chọn được tối đa ${MAX_SEATS} ghế mỗi lần đặt.`);
                return prev;
            }
            return [...prev, seat.id];
        });
    };

    const handleSubmit = async () => {
        if (!isAuthenticated) {
            toast.info("Đăng nhập để tiếp tục đặt vé.");
            router.push("/login");
            return;
        }
        if (!selectedIds.length) {
            toast.warning("Chọn ít nhất một ghế.");
            return;
        }

        try {
            const booking = await createBooking.mutateAsync({
                showtime_id: showtimeId,
                seat_ids: selectedIds,
            });
            router.push(`/payment/${booking.id}`);
        } catch {
            toast.error("Không giữ được ghế", {
                description: "Có thể người khác vừa đặt mất. Chọn ghế khác rồi thử lại.",
            });
            setSelectedIds([]);
        }
    };

    if (loadingShowtime || loadingSeats) return <BookingSkeleton />;

    if (!showtime || !seats?.length) {
        return (
            <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
                <Empty className="border">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Armchair />
                        </EmptyMedia>
                        <EmptyTitle>Không mở bán suất này</EmptyTitle>
                        <EmptyDescription>
                            Suất chiếu không tồn tại hoặc chưa xếp ghế.
                        </EmptyDescription>
                    </EmptyHeader>
                    <Button variant="outline" onClick={() => router.back()}>
                        Quay lại
                    </Button>
                </Empty>
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-5xl px-4 py-10 pb-32 sm:px-6 lg:pb-10">
            <header className="mb-6 flex flex-col gap-1">
                <p className="label-caps">Chọn ghế</p>
                <h1 className="text-3xl sm:text-4xl">
                    {showtime.movie?.title ?? "Suất chiếu"}
                </h1>
                <p className="tabular text-muted-foreground">
                    {formatDate(showtime.start_time)} · {formatTime(showtime.start_time)}–
                    {formatTime(showtime.end_time)}
                    {showtime.room?.name && ` · ${showtime.room.name}`}
                    {showtime.cinema?.name && ` · ${showtime.cinema.name}`}
                </p>
            </header>

            <div className="grid gap-6 lg:grid-cols-[1fr_300px] lg:items-start">
                {/* Sơ đồ ghế ngồi thẳng trên nền: nó đã là một khối hình rõ
                    ràng, bọc thêm card chỉ thêm một đường viền thừa. */}
                <div className="flex flex-col gap-6">
                        <div className="flex flex-col items-center gap-2">
                            <div
                                className="h-2 w-4/5 rounded-[50%] bg-gradient-to-b from-foreground/25 to-transparent"
                                style={{ boxShadow: "0 0 60px 10px color-mix(in oklab, var(--foreground) 12%, transparent)" }}
                            />
                            <span className="label-caps">Màn hình</span>
                        </div>

                        <div className="-mx-2 overflow-x-auto px-2">
                            <div className="mx-auto flex min-w-fit flex-col gap-1.5">
                                {rows.map(({ row, seats: rowSeats }) => (
                                    <div key={row} className="flex items-center gap-2">
                                        <span className="w-4 shrink-0 text-center text-xs text-muted-foreground tabular">
                                            {row}
                                        </span>
                                        <div className="flex gap-1.5">
                                            {rowSeats.map((seat) => (
                                                <SeatButton
                                                    key={seat.id}
                                                    seat={seat}
                                                    selected={selectedIds.includes(seat.id)}
                                                    onToggle={() => toggleSeat(seat)}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex flex-wrap gap-x-5 gap-y-2.5 border-t pt-5 text-xs text-muted-foreground">
                            <Legend state="available" label="Trống" />
                            <Legend state="booked" label="Đã đặt" />
                            <Legend state="locked" label="Người khác đang giữ" />
                            <Legend state="selected" label="Bạn chọn" />
                        </div>
                </div>

                <Card className="surface-soft max-lg:fixed max-lg:inset-x-0 max-lg:bottom-0 max-lg:z-40 max-lg:rounded-none max-lg:shadow-none lg:sticky lg:top-20">
                    <CardHeader className="max-lg:hidden">
                        <CardTitle className="text-base">Đơn của bạn</CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-3">
                        {selectedSeats.length ? (
                            <>
                                <div className="flex flex-wrap gap-1.5 max-lg:hidden">
                                    {selectedSeats.map((seat) => (
                                        <Badge key={seat.id} variant="secondary" className="code">
                                            {seatLabel(seat)}
                                            <span className="ml-1 font-normal opacity-70">
                                                {SEAT_TYPE_LABEL[seat.seat_type]}
                                            </span>
                                        </Badge>
                                    ))}
                                </div>
                                <div className="flex items-baseline justify-between gap-3">
                                    <span className="text-sm text-muted-foreground">
                                        {selectedSeats.length} ghế
                                        <span className="lg:hidden">
                                            {" · "}
                                            <span className="code">
                                                {selectedSeats.map(seatLabel).join(", ")}
                                            </span>
                                        </span>
                                    </span>
                                    <span className="tabular text-xl font-semibold text-primary">
                                        {formatCurrency(total)}
                                    </span>
                                </div>
                            </>
                        ) : (
                            <p className="flex items-center gap-2 text-sm text-muted-foreground">
                                <AlertCircle className="size-4 shrink-0" />
                                Chưa chọn ghế nào
                            </p>
                        )}

                        <Button
                            onClick={handleSubmit}
                            disabled={!selectedSeats.length || createBooking.isPending}
                            className="w-full"
                        >
                            {createBooking.isPending ? (
                                "Đang giữ ghế..."
                            ) : (
                                <>
                                    Tiếp tục <ArrowRight className="size-4" />
                                </>
                            )}
                        </Button>

                        <p className="flex items-center gap-1.5 text-xs text-muted-foreground max-lg:hidden">
                            <Clock className="size-3 shrink-0" />
                            Ghế được giữ 15 phút để bạn thanh toán.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function SeatButton({
    seat,
    selected,
    onToggle,
}: {
    seat: Seat;
    selected: boolean;
    onToggle: () => void;
}) {
    const status = seat.status ?? "available";
    const taken = status === "booked";
    const held = status === "locked";
    const label = seatLabel(seat);

    return (
        <button
            type="button"
            onClick={onToggle}
            disabled={taken || held}
            aria-pressed={selected}
            aria-label={`Ghế ${label}, ${SEAT_TYPE_LABEL[seat.seat_type]}, ${
                formatCurrency(toNumber(seat.final_price))
            }${taken ? ", đã đặt" : held ? ", người khác đang giữ" : ""}`}
            title={`${label} · ${SEAT_TYPE_LABEL[seat.seat_type]} · ${formatCurrency(
                toNumber(seat.final_price)
            )}`}
            className={cn(
                "rounded-seat size-7 border text-[10px] font-medium transition-colors sm:size-8",
                "focus-visible:ring-ring focus-visible:ring-[3px] focus-visible:outline-none",
                selected
                    ? SEAT_STATE.selected
                    : taken
                      ? `${SEAT_STATE.booked} cursor-not-allowed`
                      : held
                        ? `${SEAT_STATE.locked} cursor-not-allowed`
                        : `${SEAT_STATE.available} hover:border-primary hover:bg-accent`
            )}
        >
            {seat.seat_number}
        </button>
    );
}

function Legend({
    state,
    label,
}: {
    state: keyof typeof SEAT_STATE;
    label: string;
}) {
    return (
        <span className="flex items-center gap-1.5">
            {/* Cùng kích thước, cùng bo góc, cùng class với ô ghế thật. */}
            <span className={cn("rounded-seat size-3.5 border", SEAT_STATE[state])} />
            {label}
        </span>
    );
}

function BookingSkeleton() {
    return (
        <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
            <Skeleton className="mb-2 h-4 w-20" />
            <Skeleton className="mb-2 h-8 w-64" />
            <Skeleton className="mb-8 h-4 w-80" />
            <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
                <Skeleton className="h-80 rounded-xl" />
                <Skeleton className="h-44 rounded-xl" />
            </div>
        </div>
    );
}
