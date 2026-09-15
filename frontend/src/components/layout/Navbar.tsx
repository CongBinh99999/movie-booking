"use client";

import { Film, LogOut, Menu, Ticket, User as UserIcon } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { ThemeToggle } from "@/components/theme-toggle";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth.store";

const NAV_LINKS = [{ href: "/movies", label: "Phim" }];

export function Navbar() {
    const pathname = usePathname();
    const router = useRouter();
    const { user, isAuthenticated, clearAuth } = useAuthStore();
    const [sheetOpen, setSheetOpen] = useState(false);

    const handleLogout = () => {
        clearAuth();
        setSheetOpen(false);
        router.push("/");
    };

    const initial = (user?.full_name || user?.username || "?").charAt(0).toUpperCase();

    return (
        <header className="sticky top-0 z-50 border-b bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70">
            <div className="mx-auto flex h-14 max-w-7xl items-center gap-3 px-4 sm:px-6 lg:px-8">
                <Link href="/" className="flex items-center gap-2">
                    <span className="grid size-7 place-items-center rounded-md bg-primary text-primary-foreground">
                        <Film className="size-4" />
                    </span>
                    <span className="text-base font-semibold tracking-tight">CineBook</span>
                </Link>

                <nav className="ml-2 hidden items-center gap-1 md:flex">
                    {NAV_LINKS.map((link) => (
                        <Button
                            key={link.href}
                            asChild
                            variant="ghost"
                            size="sm"
                            className={cn(
                                pathname.startsWith(link.href) && "bg-accent text-accent-foreground"
                            )}
                        >
                            <Link href={link.href}>{link.label}</Link>
                        </Button>
                    ))}
                </nav>

                <div className="ml-auto flex items-center gap-1.5">
                    <ThemeToggle />

                    {isAuthenticated && user ? (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm" className="gap-2 px-2">
                                    <Avatar className="size-6">
                                        <AvatarFallback className="bg-primary text-[11px] text-primary-foreground">
                                            {initial}
                                        </AvatarFallback>
                                    </Avatar>
                                    <span className="hidden max-w-28 truncate sm:inline">
                                        {user.full_name || user.username}
                                    </span>
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-56">
                                <DropdownMenuLabel className="font-normal">
                                    <div className="truncate text-sm font-medium">
                                        {user.full_name || user.username}
                                    </div>
                                    <div className="truncate text-xs text-muted-foreground">
                                        {user.email}
                                    </div>
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem asChild>
                                    <Link href="/bookings" className="gap-2">
                                        <Ticket className="size-4" /> Vé của tôi
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuItem asChild>
                                    <Link href="/profile" className="gap-2">
                                        <UserIcon className="size-4" /> Hồ sơ
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={handleLogout} className="gap-2">
                                    <LogOut className="size-4" /> Đăng xuất
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    ) : (
                        <div className="hidden items-center gap-1.5 sm:flex">
                            <Button asChild variant="ghost" size="sm">
                                <Link href="/login">Đăng nhập</Link>
                            </Button>
                            <Button asChild size="sm">
                                <Link href="/register">Đăng ký</Link>
                            </Button>
                        </div>
                    )}

                    <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
                        <SheetTrigger asChild>
                            <Button variant="ghost" size="icon" className="md:hidden" aria-label="Mở menu">
                                <Menu className="size-4" />
                            </Button>
                        </SheetTrigger>
                        <SheetContent side="right" className="w-72">
                            <SheetHeader>
                                <SheetTitle>Menu</SheetTitle>
                            </SheetHeader>
                            <nav className="flex flex-col gap-1 px-4">
                                {NAV_LINKS.map((link) => (
                                    <Button
                                        key={link.href}
                                        asChild
                                        variant="ghost"
                                        className="justify-start"
                                        onClick={() => setSheetOpen(false)}
                                    >
                                        <Link href={link.href}>{link.label}</Link>
                                    </Button>
                                ))}

                                <Separator className="my-2" />

                                {isAuthenticated ? (
                                    <>
                                        <Button asChild variant="ghost" className="justify-start" onClick={() => setSheetOpen(false)}>
                                            <Link href="/bookings">Vé của tôi</Link>
                                        </Button>
                                        <Button asChild variant="ghost" className="justify-start" onClick={() => setSheetOpen(false)}>
                                            <Link href="/profile">Hồ sơ</Link>
                                        </Button>
                                        <Button variant="ghost" className="justify-start" onClick={handleLogout}>
                                            Đăng xuất
                                        </Button>
                                    </>
                                ) : (
                                    <>
                                        <Button asChild variant="ghost" className="justify-start" onClick={() => setSheetOpen(false)}>
                                            <Link href="/login">Đăng nhập</Link>
                                        </Button>
                                        <Button asChild className="justify-start" onClick={() => setSheetOpen(false)}>
                                            <Link href="/register">Đăng ký</Link>
                                        </Button>
                                    </>
                                )}
                            </nav>
                        </SheetContent>
                    </Sheet>
                </div>
            </div>
        </header>
    );
}
