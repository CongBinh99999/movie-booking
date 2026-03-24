import Link from "next/link";
import { Film } from "lucide-react";

export function Footer() {
    return (
        <footer className="border-t border-white/5 bg-[#0a0a0f] mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="col-span-1 md:col-span-2">
                        <Link href="/" className="flex items-center gap-2 mb-3">
                            <div className="p-1.5 bg-[#e50914] rounded-lg">
                                <Film className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold">CineBook</span>
                        </Link>
                        <p className="text-sm text-[#8888aa] leading-relaxed max-w-sm">
                            Nền tảng đặt vé xem phim trực tuyến hàng đầu Việt Nam. Trải nghiệm
                            xem phim tuyệt vời với dịch vụ đặt vé nhanh chóng và tiện lợi.
                        </p>
                    </div>
                    {/* Links */}
                    <div>
                        <h4 className="text-sm font-semibold text-white mb-3">Khám phá</h4>
                        <ul className="space-y-2">
                            {[
                                { href: "/movies", label: "Phim đang chiếu" },
                                { href: "/movies?status=coming_soon", label: "Phim sắp chiếu" },
                                { href: "/cinemas", label: "Hệ thống rạp" },
                            ].map((item) => (
                                <li key={item.href}>
                                    <Link href={item.href} className="text-sm text-[#8888aa] hover:text-white transition-colors">
                                        {item.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-sm font-semibold text-white mb-3">Tài khoản</h4>
                        <ul className="space-y-2">
                            {[
                                { href: "/login", label: "Đăng nhập" },
                                { href: "/register", label: "Đăng ký" },
                                { href: "/bookings", label: "Vé của tôi" },
                            ].map((item) => (
                                <li key={item.href}>
                                    <Link href={item.href} className="text-sm text-[#8888aa] hover:text-white transition-colors">
                                        {item.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
                <div className="mt-8 pt-6 border-t border-white/5 text-center">
                    <p className="text-xs text-[#8888aa]">
                        © {new Date().getFullYear()} CineBook. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    );
}
