"use client";

import { usePathname } from "next/navigation";

import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/layout/Navbar";

/** Trang đăng nhập / đăng ký tự dựng khung riêng, không dùng navbar + footer. */
const BARE_ROUTES = ["/login", "/register"];

export function SiteChrome({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const bare = BARE_ROUTES.some((route) => pathname.startsWith(route));

    if (bare) return <>{children}</>;

    return (
        <div className="flex min-h-dvh flex-col">
            <Navbar />
            <main className="flex-1">{children}</main>
            <Footer />
        </div>
    );
}
