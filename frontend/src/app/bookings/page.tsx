"use client";

import { CalendarDays, Ticket } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Empty,
    EmptyDescription,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
} from "@/components/ui/empty";
import { Skeleton } from "@/components/ui/skeleton";
import { useMyBookings } from "@/hooks/useBookings";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";
import { useAuthStore } from "@/store/auth.store";
import { toNumber, type Booking, type BookingStatus } from "@/types";

const STATUS: Record<
    BookingStatus,
    { label: string; className: string }
> = {
    pending: { label: "Chờ thanh toán", className: "border-[var(--warning)] text-warning" },
    confirmed: { label: "Đã xác nhận", className: "border-[var(--success)] text-success" },
    cancelled: { label: "Đã huỷ", className: "border-destructive text-destructive" },
    expired: { label: "Hết hạn", className: "text-muted-foreground" },
};

export default function BookingsPage() {
    const router = useRouter();
    const { isAuthenticated } = useAuthStore();
    const { data, isLoading, isError } = useMyBookings();

    useEffect(() => {
        if (!isAuthenticated) router.push("/login");
    }, [isAuthenticated, router]);

    if (!isAuthenticated) return null;

    const bookings = data?.items;

    return (
        <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
            <h1 className="text-3xl sm:text-4xl">Vé của tôi</h1>
            <p className="mt-1 mb-6 text-muted-foreground">
                {data ? `${data.total} đơn đặt vé` : "Đang tải danh sách vé"}
            </p>

            {isLoading ? (
                <div className="flex flex-col gap-3">
                    {[0, 1, 2].map((i) => (
                        <Skeleton key={i} className="h-24 rounded-lg" />
                    ))}
                </div>
            ) : isError ? (
                <Empty className="border">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Ticket />
                        </EmptyMedia>
                        <EmptyTitle>Không tải được danh sách vé</EmptyTitle>
                        <EmptyDescription>Tải lại trang để thử lại.</EmptyDescription>
                    </EmptyHeader>
                </Empty>
            ) : !bookings?.length ? (
                <Empty className="border">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Ticket />
                        </EmptyMedia>
                        <EmptyTitle>Chưa có vé nào</EmptyTitle>
                        <EmptyDescription>
                            Đặt vé đầu tiên để thấy nó xuất hiện ở đây.
                        </EmptyDescription>
                    </EmptyHeader>
                    <Button asChild>
                        <Link href="/movies">Xem phim đang chiếu</Link>
                    </Button>
                </Empty>
            ) : (
                <div className="flex flex-col">
                    {bookings.map((booking) => (
                        <BookingRow key={booking.id} booking={booking} />
                    ))}
                </div>
            )}
        </div>
    );
}

function BookingRow({ booking }: { booking: Booking }) {
    const status = STATUS[booking.status];

    return (
        <div className="flex flex-wrap items-start justify-between gap-4 border-b py-5 first:pt-0 last:border-b-0">
                <div className="flex min-w-0 flex-col gap-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="code text-sm font-medium">{booking.booking_code}</span>
                        <Badge variant="outline" className={status.className}>
                            {status.label}
                        </Badge>
                    </div>
                    {booking.created_at && (
                        <p className="tabular flex items-center gap-1.5 text-xs text-muted-foreground">
                            <CalendarDays className="size-3" />
                            Đặt lúc {formatTime(booking.created_at)}{" "}
                            {formatDate(booking.created_at)}
                        </p>
                    )}
                    {booking.status === "pending" && booking.expires_at && (
                        <p className="tabular text-xs text-warning">
                            Giữ ghế đến {formatTime(booking.expires_at)}
                        </p>
                    )}
                    {booking.cancellation_reason && (
                        <p className="text-xs text-muted-foreground">
                            Lý do huỷ: {booking.cancellation_reason}
                        </p>
                    )}
                </div>

                <div className="flex shrink-0 flex-col items-end gap-2">
                    <span className="tabular text-lg font-semibold">
                        {formatCurrency(toNumber(booking.total_amount))}
                    </span>
                    {booking.status === "pending" && (
                        <Button asChild size="sm">
                            <Link href={`/payment/${booking.id}`}>Thanh toán</Link>
                        </Button>
                    )}
                </div>
        </div>
    );
}
