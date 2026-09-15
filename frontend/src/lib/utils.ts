export { cn } from "cn";

import { format } from "date-fns";
import { vi } from "date-fns/locale";

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
