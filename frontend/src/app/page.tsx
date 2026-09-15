"use client";

import { ArrowRight, Clock, Film, Play } from "lucide-react";
import Link from "next/link";

import { QuickBook } from "@/components/booking/QuickBook";
import { MovieGrid } from "@/components/movies/MovieCard";
import { Poster } from "@/components/movies/Poster";
import { Button } from "@/components/ui/button";
import {
    Empty,
    EmptyDescription,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
} from "@/components/ui/empty";
import { Skeleton } from "@/components/ui/skeleton";
import { useComingSoon, useNowShowing } from "@/hooks/useMovies";
import type { Movie } from "@/types";

export default function HomePage() {
    const nowShowing = useNowShowing();
    const comingSoon = useComingSoon();

    const featured = nowShowing.data?.items[0];

    return (
        <>
            <Hero movie={featured} isLoading={nowShowing.isLoading} />

            <div className="mx-auto flex max-w-7xl flex-col gap-12 px-4 pb-20 sm:px-6 lg:px-8">
                {/* Thanh đặt vé đè lên mép hero — nó là việc chính, không phải
                    một mục nằm đâu đó giữa trang. */}
                <div className="-mt-8 sm:-mt-10">
                    <QuickBook />
                </div>

                <Section
                    title="Đang chiếu"
                    href="/movies"
                    isLoading={nowShowing.isLoading}
                    movies={nowShowing.data?.items}
                    emptyLabel="Chưa có phim nào đang chiếu."
                />
                <Section
                    title="Sắp chiếu"
                    href="/movies?status=coming_soon"
                    isLoading={comingSoon.isLoading}
                    movies={comingSoon.data?.items}
                    emptyLabel="Chưa có lịch phim sắp chiếu."
                />
            </div>
        </>
    );
}

/**
 * Hero lấy chính phim đầu tiên đang chiếu làm nền. Cột chữ bị giới hạn bề
 * rộng để không kéo dài hết màn 1920 — phần trống bên phải là chỗ cho poster,
 * không phải khoảng trắng bỏ không.
 */
function Hero({ movie, isLoading }: { movie?: Movie; isLoading: boolean }) {
    return (
        <section className="relative isolate overflow-hidden border-b pb-16 sm:pb-20">
            {movie && (
                <div className="backdrop-wash absolute inset-0 -z-20 opacity-25">
                    <Poster
                        src={movie.poster_url}
                        title={movie.title}
                        sizes="100vw"
                        priority
                        className="scale-110 blur-2xl"
                    />
                </div>
            )}
            <div className="spotlight absolute inset-0 -z-10" />

            <div className="mx-auto grid max-w-7xl gap-8 px-4 pt-12 sm:px-6 md:grid-cols-[minmax(0,1fr)_auto] md:items-center md:pt-16 lg:px-8">
                <div className="flex max-w-2xl flex-col items-start gap-4">
                    <p className="label-caps">Đang chiếu tại CineBook</p>

                    {isLoading ? (
                        <>
                            <Skeleton className="h-14 w-full max-w-lg" />
                            <Skeleton className="h-5 w-72" />
                            <Skeleton className="h-11 w-40" />
                        </>
                    ) : movie ? (
                        <>
                            <h1 className="text-4xl sm:text-5xl lg:text-6xl">{movie.title}</h1>

                            <p className="tabular flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
                                <span className="inline-flex items-center gap-1.5">
                                    <Clock className="size-3.5" />
                                    {movie.duration_minutes} phút
                                </span>
                                {movie.age_rating && (
                                    <span className="rounded border border-border-strong px-1.5 py-px text-xs font-medium">
                                        {movie.age_rating}
                                    </span>
                                )}
                                {movie.director && <span>{movie.director}</span>}
                                {movie.language && <span>{movie.language}</span>}
                            </p>

                            {movie.description && (
                                <p className="line-clamp-3 max-w-prose leading-relaxed text-muted-foreground">
                                    {movie.description}
                                </p>
                            )}

                            <div className="mt-1 flex flex-wrap gap-2.5">
                                <Button asChild size="lg">
                                    <Link href={`/movies/${movie.id}`}>
                                        <Play className="size-4" />
                                        Đặt vé ngay
                                    </Link>
                                </Button>
                                <Button asChild size="lg" variant="outline">
                                    <Link href="/movies">Tất cả phim</Link>
                                </Button>
                            </div>
                        </>
                    ) : (
                        <>
                            <h1 className="text-4xl sm:text-5xl">Chọn phim, chọn ghế, xong.</h1>
                            <p className="max-w-prose text-muted-foreground">
                                Ghế được giữ 15 phút sau khi đặt. Thanh toán qua VNPay để xác
                                nhận vé.
                            </p>
                            <Button asChild size="lg" className="mt-1">
                                <Link href="/movies">
                                    Xem phim <ArrowRight className="size-4" />
                                </Link>
                            </Button>
                        </>
                    )}
                </div>

                {movie && (
                    <Link
                        href={`/movies/${movie.id}`}
                        className="rounded-poster relative hidden aspect-[2/3] w-52 shrink-0 overflow-hidden shadow-2xl ring-1 ring-border-strong transition duration-300 hover:-translate-y-1 md:block lg:w-64"
                    >
                        <Poster src={movie.poster_url} title={movie.title} sizes="256px" priority />
                    </Link>
                )}
            </div>
        </section>
    );
}

function Section({
    title,
    href,
    movies,
    isLoading,
    emptyLabel,
}: {
    title: string;
    href: string;
    movies?: Movie[];
    isLoading: boolean;
    emptyLabel: string;
}) {
    const empty = !isLoading && !movies?.length;

    return (
        <section className="flex flex-col gap-5">
            <div className="flex items-end justify-between gap-3 border-b pb-3">
                <h2 className="text-2xl sm:text-3xl">{title}</h2>
                {!empty && (
                    <Button asChild variant="ghost" size="sm">
                        <Link href={href}>
                            Tất cả <ArrowRight className="size-4" />
                        </Link>
                    </Button>
                )}
            </div>

            {empty ? (
                <Empty className="border border-dashed">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Film />
                        </EmptyMedia>
                        <EmptyTitle>Chưa có phim</EmptyTitle>
                        <EmptyDescription>{emptyLabel}</EmptyDescription>
                    </EmptyHeader>
                </Empty>
            ) : (
                <MovieGrid movies={movies} isLoading={isLoading} skeletonCount={6} />
            )}
        </section>
    );
}
