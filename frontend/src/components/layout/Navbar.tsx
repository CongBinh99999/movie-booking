"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Film, Menu, X, User, LogOut, Ticket } from "lucide-react";
import { useAuthStore } from "@/store/auth.store";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
    { href: "/movies", label: "Phim" },
    { href: "/cinemas", label: "Rạp" },
];

export function Navbar() {
    const pathname = usePathname();
    const router = useRouter();
    const { user, isAuthenticated, clearAuth } = useAuthStore();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

    const handleLogout = () => {
        clearAuth();
        router.push("/");
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-white/5">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="p-1.5 bg-[#e50914] rounded-lg group-hover:bg-[#b20710] transition-colors duration-200">
                            <Film className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold tracking-tight">CineBook</span>
                    </Link>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center gap-1">
                        {NAV_LINKS.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={cn(
                                    "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                                    pathname.startsWith(link.href)
                                        ? "bg-white/10 text-white"
                                        : "text-[#8888aa] hover:text-white hover:bg-white/5"
                                )}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </div>

                    {/* Right Actions */}
                    <div className="hidden md:flex items-center gap-3">
                        {isAuthenticated && user ? (
                            <div className="relative">
                                <button
                                    onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                                    className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors duration-200 cursor-pointer"
                                >
                                    <div className="w-8 h-8 rounded-full bg-[#e50914] flex items-center justify-center text-white text-sm font-semibold">
                                        {user.full_name.charAt(0).toUpperCase()}
                                    </div>
                                    <span className="text-sm font-medium">{user.full_name}</span>
                                </button>
                                {isUserMenuOpen && (
                                    <div className="absolute right-0 mt-2 w-48 glass-card rounded-xl shadow-2xl border border-white/10 py-1 animate-fade-in">
                                        <Link
                                            href="/profile"
                                            className="flex items-center gap-2 px-4 py-2.5 text-sm text-[#8888aa] hover:text-white hover:bg-white/5 transition-colors"
                                            onClick={() => setIsUserMenuOpen(false)}
                                        >
                                            <User className="w-4 h-4" /> Hồ sơ
                                        </Link>
                                        <Link
                                            href="/bookings"
                                            className="flex items-center gap-2 px-4 py-2.5 text-sm text-[#8888aa] hover:text-white hover:bg-white/5 transition-colors"
                                            onClick={() => setIsUserMenuOpen(false)}
                                        >
                                            <Ticket className="w-4 h-4" /> Vé của tôi
                                        </Link>
                                        <hr className="my-1 border-white/10" />
                                        <button
                                            onClick={handleLogout}
                                            className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-white/5 transition-colors cursor-pointer"
                                        >
                                            <LogOut className="w-4 h-4" /> Đăng xuất
                                        </button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <>
                                <Link
                                    href="/login"
                                    className="px-4 py-2 text-sm font-medium text-[#8888aa] hover:text-white transition-colors duration-200"
                                >
                                    Đăng nhập
                                </Link>
                                <Link
                                    href="/register"
                                    className="px-4 py-2 text-sm font-medium bg-[#e50914] hover:bg-[#b20710] text-white rounded-lg transition-colors duration-200"
                                >
                                    Đăng ký
                                </Link>
                            </>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                        aria-label="Toggle menu"
                    >
                        {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
                <div className="md:hidden border-t border-white/5 glass-card animate-fade-in">
                    <div className="px-4 py-3 space-y-1">
                        {NAV_LINKS.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="block px-3 py-2 rounded-lg text-sm text-[#8888aa] hover:text-white hover:bg-white/5 transition-colors"
                                onClick={() => setIsMenuOpen(false)}
                            >
                                {link.label}
                            </Link>
                        ))}
                        <hr className="border-white/10 my-2" />
                        {isAuthenticated ? (
                            <button
                                onClick={handleLogout}
                                className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-white/5 rounded-lg transition-colors cursor-pointer"
                            >
                                Đăng xuất
                            </button>
                        ) : (
                            <>
                                <Link href="/login" className="block px-3 py-2 text-sm text-[#8888aa] hover:text-white hover:bg-white/5 rounded-lg transition-colors" onClick={() => setIsMenuOpen(false)}>
                                    Đăng nhập
                                </Link>
                                <Link href="/register" className="block px-3 py-2 text-sm text-white bg-[#e50914] hover:bg-[#b20710] rounded-lg transition-colors" onClick={() => setIsMenuOpen(false)}>
                                    Đăng ký
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
}
