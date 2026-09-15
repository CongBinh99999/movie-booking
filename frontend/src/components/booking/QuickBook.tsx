"use client";

import { format, isSameDay } from "date-fns";
import { vi } from "date-fns/locale";
import { CalendarDays, MapPin, Ticket } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useNowShowing } from "@/hooks/useMovies";
import { useShowtimesByMovie } from "@/hooks/useShowtimes";
import { cn, formatCurrency, formatTime } from "@/lib/utils";
import { toNumber, type Showtime } from "@/types";

const DAYS_AHEAD = 7;

/**
 * Phim → Ngày → Suất, ngay trên trang chủ.
 *
 * Đây là việc chính của cả trang web, mà bản trước chôn nó sau ba cú click
 * (trang chủ → chi tiết phim → lịch chiếu). Mọi rạp thật đều đặt bộ chọn này
 * ngay dưới hero, và đó cũng là lý do trang chủ cũ trông trống: nó không làm
 * gì ngoài việc dẫn đi chỗ khác.
 */
export function QuickBook() {
    const { data: movies, isLoading: loadingMovies } = useNowShowing();
    const [movieId, setMovieId] = useState<string>("");
    const [dayIndex, setDayIndex] = useState(0);

    const items = movies?.items;
    const selectedId = movieId || items?.[0]?.id || "";
    const { data: showtimes, isLoading: loadingShowtimes } =
        useShowtimesByMovie(selectedId);

    // Chốt mốc thời gian một lần cho cả component: Date.now() gọi trong
    // render là hàm không thuần, danh sách suất sẽ nhảy giữa các lần render.
    const [now] = useState(() => Date.now());

    const days = useMemo(() => {
        const today = new Date(now);
        return Array.from({ length: DAYS_AHEAD }, (_, i) => {
            const d = new Date(today);
            d.setDate(today.getDate() + i);
            return d;
        });
    }, [now]);

    const selectedDay = days[dayIndex];

    // Gom suất của ngày đang chọn theo rạp, bỏ suất đã qua giờ.
    const byCinema = useMemo(() => {
        const grouped = new Map<string, { name: string; items: Showtime[] }>();

        for (const st of showtimes ?? []) {
            const start = new Date(st.start_time);
            if (start.getTime() <= now) continue;
            if (!isSameDay(start, selectedDay)) continue;

            const key = st.cinema?.id ?? st.room_id;
            const name = st.cinema?.name ?? "Rạp CineBook";
            const entry = grouped.get(key) ?? { name, items: [] };
            entry.items.push(st);
            grouped.set(key, entry);
        }

        return [...grouped.values()].map((g) => ({
            ...g,
            items: g.items.sort((a, b) => a.start_time.localeCompare(b.start_time)),
        }));
    }, [showtimes, selectedDay, now]);

    const isLoading = loadingMovies || loadingShowtimes;

    return (
        <section className="surface-soft p-4 sm:p-5">
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
                <span className="label-caps flex items-center gap-1.5">
                    <Ticket className="size-3.5" />
                    Đặt vé nhanh
                </span>

                <div className="sm:ml-auto sm:w-72">
                    {loadingMovies ? (
                        <Skeleton className="h-9 w-full" />
                    ) : (
                        <Select value={selectedId} onValueChange={setMovieId}>
                            <SelectTrigger className="w-full" aria-label="Chọn phim">
                                <SelectValue placeholder="Chọn phim" />
                            </SelectTrigger>
                            <SelectContent>
                                {items?.map((movie) => (
                                    <SelectItem key={movie.id} value={movie.id}>
                                        {movie.title}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    )}
                </div>
            </div>

            {/* Dải ngày: nhãn thứ + ngày, hôm nay đứng đầu. */}
            <div className="-mx-1 mb-4 flex gap-1.5 overflow-x-auto px-1 pb-1">
                {days.map((day, i) => (
                    <button
                        key={day.toISOString()}
                        type="button"
                        onClick={() => setDayIndex(i)}
                        aria-pressed={i === dayIndex}
                        className={cn(
                            "rounded-control flex min-w-14 shrink-0 flex-col items-center gap-0.5 border px-3 py-2 transition-colors",
                            "focus-visible:ring-ring focus-visible:ring-[3px] focus-visible:outline-none",
                            i === dayIndex
                                ? "border-transparent bg-primary text-primary-foreground"
                                : "border-border-strong hover:bg-accent"
                        )}
                    >
                        <span className="text-[0.625rem] font-medium tracking-wide uppercase opacity-80">
                            {i === 0 ? "Hôm nay" : format(day, "EEE", { locale: vi })}
                        </span>
                        <span className="tabular text-sm font-semibold">
                            {format(day, "dd/MM")}
                        </span>
                    </button>
                ))}
            </div>

            {isLoading ? (
                <div className="flex gap-2">
                    {[0, 1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-9 w-20" />
                    ))}
                </div>
            ) : byCinema.length ? (
                <div className="flex flex-col gap-4">
                    {byCinema.map((cinema) => (
                        <div key={cinema.name} className="flex flex-col gap-2">
                            <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                                <MapPin className="size-3.5" />
                                {cinema.name}
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {cinema.items.map((st) => (
                                    <Button
                                        key={st.id}
                                        asChild
                                        variant="outline"
                                        size="sm"
                                        className="rounded-control h-auto flex-col items-start gap-0 px-3 py-1.5"
                                    >
                                        <Link href={`/booking/${st.id}`}>
                                            <span className="tabular text-sm font-semibold">
                                                {formatTime(st.start_time)}
                                            </span>
                                            <span className="tabular text-[0.6875rem] font-normal text-muted-foreground">
                                                {formatCurrency(toNumber(st.base_price))}
                                            </span>
                                        </Link>
                                    </Button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="flex items-center gap-2 py-2 text-sm text-muted-foreground">
                    <CalendarDays className="size-4 shrink-0" />
                    Không còn suất nào trong ngày {format(selectedDay, "dd/MM")}. Thử ngày khác.
                </p>
            )}
        </section>
    );
}
