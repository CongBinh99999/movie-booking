"use client";

import { Clock, CreditCard, Ticket } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect } from "react";
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
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useBooking } from "@/hooks/useBookings";
import { useCreateVNPayPayment } from "@/hooks/usePayment";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";
import { useAuthStore } from "@/store/auth.store";
import { toNumber } from "@/types";

const STATUS_NOTE = {
    confirmed: "Đơn này đã được xác nhận, không cần thanh toán lại.",
    cancelled: "Đơn này đã bị huỷ.",
    expired: "Đơn này đã hết hạn giữ ghế.",
} as const;

export default function PaymentPage({
    params,
}: {
    params: Promise<{ bookingId: string }>;
}) {
    const { bookingId } = use(params);
    const router = useRouter();
    const { isAuthenticated } = useAuthStore();
    const { data: booking, isLoading, isError } = useBooking(bookingId);
    const createPayment = useCreateVNPayPayment();

    useEffect(() => {
        if (!isAuthenticated) router.push("/login");
    }, [isAuthenticated, router]);

    if (!isAuthenticated) return null;

    const handlePay = async () => {
        try {
            const { payment_url } = await createPayment.mutateAsync(bookingId);
            window.location.href = payment_url;
        } catch {
            toast.error("Không tạo được giao dịch", {
                description: "Đơn có thể đã hết hạn hoặc đã được xử lý.",
            });
        }
    };

    if (isLoading) {
        return (
            <div className="mx-auto max-w-lg px-4 py-10 sm:px-6">
                <Skeleton className="mb-6 h-8 w-40" />
                <Skeleton className="h-64 rounded-xl" />
            </div>
        );
    }

    if (isError || !booking) {
        return (
            <div className="mx-auto max-w-lg px-4 py-16 sm:px-6">
                <Empty className="border">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Ticket />
                        </EmptyMedia>
                        <EmptyTitle>Không tìm thấy đơn</EmptyTitle>
                        <EmptyDescription>
                            Đơn đặt vé này không tồn tại hoặc không thuộc về bạn.
                        </EmptyDescription>
                    </EmptyHeader>
                    <Button asChild variant="outline">
                        <Link href="/bookings">Về danh sách vé</Link>
                    </Button>
                </Empty>
            </div>
        );
    }

    const payable = booking.status === "pending";

    return (
        <div className="mx-auto max-w-lg px-4 py-10 sm:px-6">
            <header className="mb-6 flex flex-col gap-1">
                <p className="label-caps">Thanh toán</p>
                <h1 className="text-2xl font-semibold">Xác nhận đơn đặt vé</h1>
            </header>

            <Card>
                <CardHeader className="flex-row items-center justify-between gap-3 space-y-0">
                    <CardTitle className="code text-base">{booking.booking_code}</CardTitle>
                    {!payable && <Badge variant="secondary">Không thanh toán được</Badge>}
                </CardHeader>

                <CardContent className="flex flex-col gap-4">
                    <dl className="flex flex-col">
                        <Row label="Số tiền">
                            <span className="tabular text-xl font-semibold text-primary">
                                {formatCurrency(toNumber(booking.total_amount))}
                            </span>
                        </Row>
                        {booking.created_at && (
                            <Row label="Đặt lúc">
                                <span className="tabular">
                                    {formatTime(booking.created_at)} {formatDate(booking.created_at)}
                                </span>
                            </Row>
                        )}
                        {payable && (
                            <Row label="Giữ ghế đến">
                                <span className="tabular inline-flex items-center gap-1.5 text-warning">
                                    <Clock className="size-3.5" />
                                    {formatTime(booking.expires_at)}
                                </span>
                            </Row>
                        )}
                    </dl>

                    <Separator />

                    {payable ? (
                        <>
                            <Button
                                onClick={handlePay}
                                disabled={createPayment.isPending}
                                size="lg"
                                className="w-full"
                            >
                                <CreditCard className="size-4" />
                                {createPayment.isPending
                                    ? "Đang chuyển hướng..."
                                    : "Thanh toán qua VNPay"}
                            </Button>
                            <p className="text-center text-xs text-muted-foreground">
                                Bạn sẽ được chuyển sang cổng VNPay để hoàn tất.
                            </p>
                        </>
                    ) : (
                        <>
                            <p className="text-sm text-muted-foreground">
                                {STATUS_NOTE[booking.status as keyof typeof STATUS_NOTE] ??
                                    "Đơn này không ở trạng thái chờ thanh toán."}
                            </p>
                            <Button asChild variant="outline" className="w-full">
                                <Link href="/bookings">Xem vé của tôi</Link>
                            </Button>
                        </>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
    return (
        <div className="flex items-baseline justify-between gap-3 border-b py-2.5 last:border-b-0">
            <dt className="text-sm text-muted-foreground">{label}</dt>
            <dd className="text-sm">{children}</dd>
        </div>
    );
}
