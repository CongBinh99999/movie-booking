"use client";

import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState, type ComponentType } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { paymentService } from "@/services/payment.service";
import { cn } from "@/lib/utils";

type State = "checking" | "success" | "failed" | "invalid";

const VIEW: Record<
    Exclude<State, "checking">,
    { icon: ComponentType<{ className?: string }>; tone: string; title: string; body: string }
> = {
    success: {
        icon: CheckCircle2,
        tone: "text-success",
        title: "Thanh toán thành công",
        body: "Vé của bạn đã được xác nhận.",
    },
    failed: {
        icon: XCircle,
        tone: "text-destructive",
        title: "Thanh toán không thành công",
        body: "Giao dịch bị huỷ hoặc bị từ chối. Bạn có thể thử lại từ trang vé.",
    },
    invalid: {
        icon: AlertTriangle,
        tone: "text-warning",
        title: "Không xác thực được giao dịch",
        body: "Chữ ký không hợp lệ. Kiểm tra lại trạng thái trong mục vé của bạn.",
    },
};

function PaymentResult() {
    const searchParams = useSearchParams();
    const [state, setState] = useState<State>("checking");

    useEffect(() => {
        // Không tin vnp_ResponseCode trên URL — người dùng sửa được.
        // Chỉ backend kiểm HMAC mới nói được giao dịch có thật hay không.
        const params = new URLSearchParams(searchParams.toString());
        paymentService
            .verifyVNPayReturn(params)
            .then(({ is_valid, is_success }) =>
                setState(!is_valid ? "invalid" : is_success ? "success" : "failed")
            )
            .catch(() => setState("invalid"));
    }, [searchParams]);

    return (
        <div className="mx-auto max-w-md px-4 py-16 sm:px-6">
            <Card>
                <CardContent className="flex flex-col items-center gap-4 text-center">
                    {state === "checking" ? (
                        <>
                            <Spinner className="size-9 text-primary" />
                            <h1 className="text-xl font-semibold">Đang xác thực giao dịch</h1>
                            <p className="text-sm text-muted-foreground">
                                Vui lòng không đóng trang này.
                            </p>
                        </>
                    ) : (
                        <Result state={state} />
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

function Result({ state }: { state: Exclude<State, "checking"> }) {
    const { icon: Icon, tone, title, body } = VIEW[state];
    return (
        <>
            <Icon className={cn("size-11", tone)} />
            <h1 className="text-xl font-semibold">{title}</h1>
            <p className="text-sm text-muted-foreground">{body}</p>
            <Button asChild className="mt-1">
                <Link href="/bookings">Xem vé của tôi</Link>
            </Button>
        </>
    );
}

export default function PaymentResultPage() {
    return (
        <Suspense fallback={null}>
            <PaymentResult />
        </Suspense>
    );
}
