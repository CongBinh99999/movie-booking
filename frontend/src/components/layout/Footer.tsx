import { Film } from "lucide-react";
import Link from "next/link";

const COLUMNS = [
    {
        title: "Khám phá",
        links: [
            { href: "/movies", label: "Phim đang chiếu" },
            { href: "/movies?status=coming_soon", label: "Phim sắp chiếu" },
        ],
    },
    {
        title: "Tài khoản",
        links: [
            { href: "/bookings", label: "Vé của tôi" },
            { href: "/profile", label: "Hồ sơ" },
            { href: "/login", label: "Đăng nhập" },
        ],
    },
];

export function Footer() {
    return (
        <footer className="mt-16 border-t">
            <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 lg:px-8 md:grid-cols-[1.6fr_1fr_1fr]">
                <div>
                    <Link href="/" className="mb-3 inline-flex items-center gap-2">
                        <span className="grid size-7 place-items-center rounded-md bg-primary text-primary-foreground">
                            <Film className="size-4" />
                        </span>
                        <span className="text-base font-semibold tracking-tight">CineBook</span>
                    </Link>
                    <p className="max-w-sm text-sm text-muted-foreground">
                        Đặt vé xem phim trực tuyến. Chọn phim, chọn ghế, thanh toán — xong trong
                        vài bước.
                    </p>
                </div>

                {COLUMNS.map((column) => (
                    <div key={column.title}>
                        <h2 className="mb-3 text-sm font-semibold">{column.title}</h2>
                        <ul className="flex flex-col gap-2">
                            {column.links.map((link) => (
                                <li key={link.href}>
                                    <Link
                                        href={link.href}
                                        className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                                    >
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>

            <div className="border-t">
                <p className="mx-auto max-w-7xl px-4 py-5 text-xs text-muted-foreground sm:px-6">
                    © {new Date().getFullYear()} CineBook
                </p>
            </div>
        </footer>
    );
}
