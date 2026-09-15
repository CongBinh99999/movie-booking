import Image from "next/image";

import { cn } from "@/lib/utils";

/**
 * Ảnh poster, và khi không có ảnh thì KHÔNG rơi về hộp xám.
 *
 * Seed hiện tại không có `poster_url`, mà poster chiếm phần lớn diện tích
 * mọi trang — để trống thành ô xám là lý do lớn nhất khiến trang trông chết.
 * Thay vào đó sinh một tấm nền gradient tất định từ chính tên phim: cùng một
 * phim luôn ra cùng một màu, khác phim thì khác màu, nên lưới phim đọc như
 * một dãy bìa đĩa chứ không phải dãy placeholder.
 */

// Bốn hướng màu, tránh xanh lá (dễ ra màu quân đội ở nền tối).
const HUES = [18, 274, 232, 336, 48, 196];

function hashOf(value: string): number {
    let hash = 0;
    for (let i = 0; i < value.length; i++) {
        hash = (hash * 31 + value.charCodeAt(i)) | 0;
    }
    return Math.abs(hash);
}

/** Chữ cái đầu, bỏ qua mạo từ để "The Batman" ra B chứ không ra T. */
function initialOf(title: string): string {
    const words = title.trim().split(/\s+/);
    const skip = new Set(["the", "a", "an", "những", "cái"]);
    const word = words.find((w) => !skip.has(w.toLowerCase())) ?? words[0] ?? "?";
    return word.charAt(0).toUpperCase();
}

export function Poster({
    src,
    title,
    className,
    sizes,
    priority,
}: {
    src: string | null;
    title: string;
    className?: string;
    sizes?: string;
    priority?: boolean;
}) {
    if (src) {
        return (
            <Image
                src={src}
                alt={`Poster phim ${title}`}
                fill
                sizes={sizes}
                priority={priority}
                className={cn("object-cover", className)}
            />
        );
    }

    const hash = hashOf(title);
    const hue = HUES[hash % HUES.length];
    const secondHue = HUES[(hash >> 3) % HUES.length];
    const tilt = 120 + (hash % 60);

    return (
        <div
            aria-label={`Phim ${title}`}
            role="img"
            className={cn("relative isolate size-full overflow-hidden", className)}
            style={{
                backgroundImage: `linear-gradient(${tilt}deg,
                    oklch(0.42 0.13 ${hue}),
                    oklch(0.24 0.08 ${secondHue}) 62%,
                    oklch(0.16 0.04 ${secondHue}))`,
            }}
        >
            {/* Chữ cái lớn tràn khung, cắt bớt ở mép — đọc như đồ hoạ bìa,
                không phải như một icon placeholder đặt giữa ô. */}
            <span
                aria-hidden
                className="font-display absolute -right-[8%] -bottom-[14%] leading-none font-extrabold text-white/12 select-none"
                style={{ fontSize: "min(11rem, 128%)" }}
            >
                {initialOf(title)}
            </span>

            <span className="absolute inset-x-0 bottom-0 line-clamp-3 bg-gradient-to-t from-black/55 to-transparent px-2.5 pt-8 pb-2.5 text-[0.8125rem] leading-tight font-semibold text-white/95">
                {title}
            </span>
        </div>
    );
}
