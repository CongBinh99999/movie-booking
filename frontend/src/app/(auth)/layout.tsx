import { Film } from "lucide-react";
import Link from "next/link";

import { PosterWall } from "@/components/auth/PosterWall";
import { ThemeToggle } from "@/components/theme-toggle";

/**
 * Khung chia đôi cho đăng nhập / đăng ký.
 *
 * Bản trước là một card nhỏ thả giữa màn 1920 với navbar và footer đầy đủ ở
 * trên dưới — phần lớn màn hình là khoảng đen. Giờ cột trái giữ chữ và form,
 * cột phải là mảng poster lấp đầy chiều cao. Không navbar, không footer: hai
 * trang này chỉ có một việc.
 */
export default function AuthLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="relative min-h-dvh lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] xl:grid-cols-[minmax(0,1fr)_1.1fr]">
            {/* Quầng sáng mờ sau cột trái, giữ cho nền không phẳng lì. */}
            <div className="spotlight pointer-events-none absolute inset-0 -z-10 lg:right-1/2" />

            <div className="flex flex-col px-5 py-6 sm:px-8 lg:px-12 xl:px-20">
                <div className="flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2">
                        <span className="grid size-8 place-items-center rounded-lg bg-primary text-primary-foreground">
                            <Film className="size-4" />
                        </span>
                        <span className="text-lg font-semibold tracking-tight">CineBook</span>
                    </Link>
                    <ThemeToggle />
                </div>

                <div className="flex flex-1 items-center justify-center py-10">
                    <div className="w-full max-w-[26rem]">{children}</div>
                </div>
            </div>

            <div className="hidden p-4 lg:block">
                <PosterWall />
            </div>
        </div>
    );
}
