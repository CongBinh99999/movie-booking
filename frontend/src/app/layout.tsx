import type { Metadata } from "next";
import { Be_Vietnam_Pro, Bricolage_Grotesque, JetBrains_Mono } from "next/font/google";

import "./globals.css";
import { Providers } from "./providers";
import { SiteChrome } from "@/components/layout/SiteChrome";
import { cn } from "@/lib/utils";

// subset "vietnamese" là bắt buộc: thiếu nó thì dấu tiếng Việt rơi về font
// hệ thống và chữ có dấu lệch hẳn so với chữ không dấu trên cùng một dòng.
const sans = Be_Vietnam_Pro({
    subsets: ["latin", "vietnamese"],
    weight: ["400", "500", "600", "700"],
    variable: "--font-sans",
    display: "swap",
});

// Chỉ dùng cho tiêu đề. Bricolage có optical size biến thiên nên ở cỡ lớn
// nó siết lại và sắc cạnh — đó là phần tương phản biên tập mà một mình
// Be Vietnam Pro không tạo ra được.
const display = Bricolage_Grotesque({
    subsets: ["latin", "vietnamese"],
    weight: ["600", "700", "800"],
    variable: "--font-display",
    display: "swap",
});

// Chỉ dùng cho mã đơn và mã ghế, nơi cần phân biệt 0/O và 1/l.
const mono = JetBrains_Mono({
    subsets: ["latin"],
    variable: "--font-mono",
    display: "swap",
});

export const metadata: Metadata = {
    title: {
        default: "CineBook — Đặt vé xem phim online",
        template: "%s | CineBook",
    },
    description:
        "Đặt vé xem phim nhanh chóng, tiện lợi tại CineBook. Chọn phim, chọn ghế, trả tiền — mọi thứ chỉ trong vài bước.",
    keywords: ["đặt vé phim", "xem phim", "rạp chiếu phim", "CineBook"],
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="vi" suppressHydrationWarning>
            <body className={cn(sans.variable, display.variable, mono.variable, "min-h-dvh")}>
                <Providers>
                    <SiteChrome>{children}</SiteChrome>
                </Providers>
            </body>
        </html>
    );
}
