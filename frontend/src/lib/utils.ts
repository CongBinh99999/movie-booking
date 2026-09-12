import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format } from "date-fns";
import { vi } from "date-fns/locale";

/** Gộp class Tailwind, class sau thắng class trước khi trùng nhóm. */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
    return new Intl.NumberFormat("vi-VN", {
        style: "currency",
        currency: "VND",
        maximumFractionDigits: 0,
    }).format(amount);
}

export function formatDate(value: string): string {
    return format(new Date(value), "dd/MM/yyyy", { locale: vi });
}

export function formatTime(value: string): string {
    return format(new Date(value), "HH:mm", { locale: vi });
}
