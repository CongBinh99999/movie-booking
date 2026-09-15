import { Label } from "@/components/ui/label";

/**
 * Một dòng nhập liệu: nhãn — chú thích — ô nhập — lỗi, xếp dọc.
 *
 * Bản trước đặt chú thích nằm NGANG HÀNG với nhãn ("Mật khẩu — Tối thiểu 8 ký
 * tự…"): trên màn hẹp nó đẩy nhãn xuống hai dòng, và vì cùng cỡ chữ nên mắt
 * đọc cả cụm thành một tiêu đề dài thay vì "tên trường + ghi chú".
 *
 * Giờ chú thích xuống dòng riêng, nhỏ hơn và nhạt hơn hẳn — thứ bậc rõ bằng
 * cỡ chữ và độ đậm, không phải bằng dấu gạch ngang.
 */
export function FieldRow({
    id,
    label,
    hint,
    error,
    children,
}: {
    id: string;
    label: string;
    hint?: string;
    error?: string;
    children: React.ReactNode;
}) {
    const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined;

    return (
        <div className="flex flex-col gap-1.5">
            <Label htmlFor={id} className="text-sm font-medium">
                {label}
            </Label>

            {hint && !error && (
                <p id={`${id}-hint`} className="text-xs leading-snug text-muted-foreground/75">
                    {hint}
                </p>
            )}

            <div aria-describedby={describedBy}>{children}</div>

            {error && (
                <p id={`${id}-error`} className="text-xs text-destructive">
                    {error}
                </p>
            )}
        </div>
    );
}
