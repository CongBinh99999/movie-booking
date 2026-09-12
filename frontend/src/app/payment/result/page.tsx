"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { AlertCircle, CheckCircle2, Loader2, XCircle } from "lucide-react";
import { paymentService } from "@/services/payment.service";

type State = "checking" | "success" | "failed" | "invalid";

function PaymentResult() {
    const searchParams = useSearchParams();
    const [state, setState] = useState<State>("checking");

    useEffect(() => {
        // VNPay redirect về đây kèm query string đã ký. Chữ ký phải được backend
        // xác thực — không tin vnp_ResponseCode trên URL.
        const params = new URLSearchParams(searchParams.toString());
        paymentService
            .verifyVNPayReturn(params)
            .then(({ is_valid, is_success }) =>
                setState(!is_valid ? "invalid" : is_success ? "success" : "failed")
            )
            .catch(() => setState("invalid"));
    }, [searchParams]);

    const view = {
        checking: {
            icon: <Loader2 className="w-12 h-12 text-[#e50914] animate-spin" />,
            title: "Đang xác thực giao dịch",
            body: "Vui lòng không đóng trang này.",
        },
        success: {
            icon: <CheckCircle2 className="w-12 h-12 text-green-400" />,
            title: "Thanh toán thành công",
            body: "Vé của bạn đã được xác nhận.",
        },
        failed: {
            icon: <XCircle className="w-12 h-12 text-red-400" />,
            title: "Thanh toán không thành công",
            body: "Giao dịch bị hủy hoặc bị từ chối. Bạn có thể thử lại.",
        },
        invalid: {
            icon: <AlertCircle className="w-12 h-12 text-yellow-400" />,
            title: "Không xác thực được giao dịch",
            body: "Chữ ký không hợp lệ. Vui lòng kiểm tra lại trong mục vé của bạn.",
        },
    }[state];

    return (
        <div className="pt-16 pb-12 min-h-screen">
            <div className="max-w-lg mx-auto px-4 sm:px-6 py-8 animate-fade-in">
                <div className="glass-card rounded-2xl p-8 flex flex-col items-center text-center gap-4">
                    {view.icon}
                    <h1 className="text-xl font-bold text-white">{view.title}</h1>
                    <p className="text-[#8888aa] text-sm">{view.body}</p>

                    {state !== "checking" && (
                        <Link
                            href="/bookings"
                            className="mt-2 px-5 py-2.5 rounded-xl bg-[#e50914] text-white text-sm
                                       font-medium hover:bg-[#c40812] transition-colors"
                        >
                            Xem vé của tôi
                        </Link>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function PaymentResultPage() {
    return (
        <Suspense fallback={null}>
            <PaymentResult />
        </Suspense>
    );
}
