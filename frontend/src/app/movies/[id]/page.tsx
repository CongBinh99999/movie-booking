"use client";

import { format } from "date-fns";
import { vi } from "date-fns/locale";
import { CalendarDays, Clock, Film, Languages, User } from "lucide-react";
import Link from "next/link";
import { use, useState } from "react";

import { Poster } from "@/components/movies/Poster";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Empty,
    EmptyDescription,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
} from "@/components/ui/empty";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useMovie } from "@/hooks/useMovies";
import { useShowtimesByMovie } from "@/hooks/useShowtimes";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";
import { getMovieStatus, toNumber, type Showtime } from "@/types";

const STATUS_LABEL = {
    now_showing: "Đang chiếu",
    coming_soon: "Sắp chiếu",
    ended: "Đã kết thúc",
} as const;

export default function MovieDetailPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const { id } = use(params);
    const { data: movie, isLoading, isError } = useMovie(id);
    const { data: showtimes, isLoading: loadingShowtimes } = useShowtimesByMovie(id);

    if (isLoading) return <MovieDetailSkeleton />;

    if (isError || !movie) {
        return (
            <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
                <Empty className="border">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Film />
                        </EmptyMedia>
                        <EmptyTitle>Không tìm thấy phim</EmptyTitle>
                        <EmptyDescription>
                            Phim này có thể đã bị gỡ khỏi hệ thống.
                        </EmptyDescription>
                    </EmptyHeader>
                    <Button asChild variant="outline">
                        <Link href="/movies">Về danh sách phim</Link>
                    </Button>
                </Empty>
            </div>
        );
    }

    const status = getMovieStatus(movie);
    const facts = [
        { icon: Clock, label: "Thời lượng", value: `${movie.duration_minutes} phút` },
        movie.release_date && {
            icon: CalendarDays,
            label: "Khởi chiếu",
            value: formatDate(movie.release_date),
        },
        movie.director && { icon: User, label: "Đạo diễn", value: movie.director },
        movie.language && {
            icon: Languages,
            label: "Ngôn ngữ",
            value: movie.subtitle ? `${movie.language} · ${movie.subtitle}` : movie.language,
        },
    ].filter(Boolean) as { icon: typeof Clock; label: string; value: string }[];

    return (
        <div className="relative isolate">
            {/* Vệt poster mờ hắt xuống, nhạt dần — cho trang có không khí thay
                vì để nội dung nổi trên nền phẳng. */}
            <div className="backdrop-wash absolute inset-x-0 top-0 -z-20 h-96 opacity-20">
                <Poster src={movie.poster_url} title={movie.title} sizes="100vw" className="scale-110 blur-3xl" />
            </div>

            <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
            <div className="grid gap-8 md:grid-cols-[260px_1fr]">
                <div className="rounded-poster relative mx-auto aspect-[2/3] w-48 overflow-hidden bg-muted shadow-xl ring-1 ring-border-strong md:mx-0 md:w-full">
                    <Poster
                        src={movie.poster_url}
                        title={movie.title}
                        sizes="(max-width: 768px) 12rem, 260px"
                        priority
                    />
                </div>

                <div className="flex flex-col gap-5">
                    <div className="flex flex-col gap-2">
                        <div className="flex flex-wrap items-center gap-2">
                            <Badge variant={status === "now_showing" ? "default" : "secondary"}>
                                {STATUS_LABEL[status]}
                            </Badge>
                            {movie.age_rating && (
                                <Badge variant="outline">{movie.age_rating}</Badge>
                            )}
                        </div>
                        <h1 className="text-4xl sm:text-5xl">{movie.title}</h1>
                        {movie.original_title && movie.original_title !== movie.title && (
                            <p className="text-muted-foreground">{movie.original_title}</p>
                        )}
                    </div>

                    <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4">
                        {facts.map(({ icon: Icon, label, value }) => (
                            <div key={label} className="flex flex-col gap-0.5">
                                <dt className="label-caps flex items-center gap-1.5">
                                    <Icon className="size-3" />
                                    {label}
                                </dt>
                                <dd className="text-sm font-medium tabular">{value}</dd>
                            </div>
                        ))}
                    </dl>

                    {movie.description && (
                        <>
                            <Separator />
                            <p className="max-w-prose leading-relaxed text-muted-foreground">
                                {movie.description}
                            </p>
                        </>
                    )}

                    {movie.cast_members.length > 0 && (
                        <div className="flex flex-col gap-2">
                            <h2 className="label-caps">Diễn viên</h2>
                            <div className="flex flex-wrap gap-1.5">
                                {movie.cast_members.map((name) => (
                                    <Badge key={name} variant="secondary" className="font-normal">
                                        {name}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <section className="mt-14">
                <h2 className="mb-5 text-2xl">Lịch chiếu</h2>
                <ShowtimeSchedule showtimes={showtimes} isLoading={loadingShowtimes} />
            </section>
            </div>
        </div>
    );
}

function ShowtimeSchedule({
    showtimes,
    isLoading,
}: {
    showtimes?: Showtime[];
    isLoading: boolean;
}) {
    // Chốt mốc thời gian một lần: gọi Date.now() mỗi lần render là hàm không
    // thuần, và danh sách sẽ nhảy giữa các lần render.
    const [now] = useState(() => Date.now());

    if (isLoading) {
        return (
            <div className="flex flex-col gap-6">
                {[0, 1].map((i) => (
                    <div key={i} className="flex flex-col gap-3">
                        <Skeleton className="h-4 w-40" />
                        <div className="flex gap-2">
                            {[0, 1, 2, 3].map((j) => (
                                <Skeleton className="h-14 w-24" key={j} />
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    const upcoming = (showtimes ?? []).filter(
        (s) => new Date(s.start_time).getTime() > now
    );

    if (!upcoming.length) {
        return (
            <Empty className="border">
                <EmptyHeader>
                    <EmptyMedia variant="icon">
                        <CalendarDays />
                    </EmptyMedia>
                    <EmptyTitle>Chưa có suất chiếu</EmptyTitle>
                    <EmptyDescription>
                        Phim này chưa được xếp lịch. Quay lại sau nhé.
                    </EmptyDescription>
                </EmptyHeader>
            </Empty>
        );
    }

    // Nhóm theo ngày để không đổ một dãy giờ dài không đầu không cuối.
    const byDay = new Map<string, Showtime[]>();
    for (const showtime of upcoming) {
        const day = showtime.start_time.slice(0, 10);
        byDay.set(day, [...(byDay.get(day) ?? []), showtime]);
    }

    return (
        <div className="flex flex-col gap-4">
            {[...byDay.entries()]
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([day, items]) => (
                    <div key={day} className="flex flex-col gap-3 border-t py-5 first:border-t-0 first:pt-0">
                        <h3 className="label-caps capitalize">
                            {format(new Date(day), "EEEE, dd/MM/yyyy", { locale: vi })}
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {items
                                .sort((a, b) => a.start_time.localeCompare(b.start_time))
                                .map((showtime) => (
                                    <Button
                                        key={showtime.id}
                                        asChild
                                        variant="outline"
                                        className="h-auto flex-col items-start gap-0.5 py-2"
                                    >
                                        <Link href={`/booking/${showtime.id}`}>
                                            <span className="tabular font-semibold">
                                                {formatTime(showtime.start_time)}
                                            </span>
                                            <span className="text-xs font-normal text-muted-foreground">
                                                {showtime.room?.name ?? "Phòng chiếu"} ·{" "}
                                                {formatCurrency(toNumber(showtime.base_price))}
                                            </span>
                                        </Link>
                                    </Button>
                                ))}
                        </div>
                    </div>
                ))}
        </div>
    );
}

function MovieDetailSkeleton() {
    return (
        <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
            <div className="grid gap-8 md:grid-cols-[260px_1fr]">
                <Skeleton className="mx-auto aspect-[2/3] w-48 rounded-lg md:mx-0 md:w-full" />
                <div className="flex flex-col gap-4">
                    <Skeleton className="h-6 w-24" />
                    <Skeleton className="h-10 w-2/3" />
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-20 w-full" />
                </div>
            </div>
        </div>
    );
}
