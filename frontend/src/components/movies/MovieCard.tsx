import Link from "next/link";

import { Poster } from "@/components/movies/Poster";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate } from "@/lib/utils";
import { getMovieStatus, type Movie } from "@/types";

/**
 * Không bọc trong Card. Poster tự nó đã là một khối đặc có mép rõ; thêm viền
 * và shadow quanh nó chỉ tạo ra hai đường kẻ song song và làm lưới trông như
 * bảng điều khiển. Tiêu đề nằm thẳng trên nền.
 */
export function MovieCard({ movie }: { movie: Movie }) {
    const status = getMovieStatus(movie);

    return (
        <Link href={`/movies/${movie.id}`} className="group flex flex-col gap-2.5">
            <div className="rounded-poster relative aspect-[2/3] overflow-hidden bg-muted ring-1 ring-border transition duration-300 group-hover:-translate-y-1 group-hover:ring-primary/70">
                <Poster
                    src={movie.poster_url}
                    title={movie.title}
                    sizes="(max-width: 640px) 45vw, (max-width: 1024px) 30vw, 220px"
                    className="transition-transform duration-500 group-hover:scale-[1.04]"
                />

                {status === "coming_soon" && (
                    <span className="absolute top-2 left-2 rounded-full bg-background/85 px-2 py-0.5 text-[0.6875rem] font-semibold backdrop-blur-sm">
                        Sắp chiếu
                    </span>
                )}
            </div>

            <div className="flex flex-col gap-0.5">
                <h3 className="line-clamp-1 text-sm leading-snug font-semibold tracking-tight transition-colors group-hover:text-brand">
                    {movie.title}
                </h3>
                <p className="tabular text-xs text-muted-foreground">
                    {movie.release_date ? formatDate(movie.release_date) : "Chưa có lịch"}
                    {" · "}
                    {movie.duration_minutes} phút
                    {movie.age_rating && ` · ${movie.age_rating}`}
                </p>
            </div>
        </Link>
    );
}

export function MovieCardSkeleton() {
    return (
        <div className="flex flex-col gap-2.5">
            <Skeleton className="rounded-poster aspect-[2/3]" />
            <Skeleton className="h-4 w-4/5" />
            <Skeleton className="h-3 w-1/3" />
        </div>
    );
}

export function MovieGrid({
    movies,
    isLoading,
    skeletonCount = 6,
}: {
    movies?: Movie[];
    isLoading?: boolean;
    skeletonCount?: number;
}) {
    return (
        <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
            {isLoading
                ? Array.from({ length: skeletonCount }, (_, i) => <MovieCardSkeleton key={i} />)
                : movies?.map((movie) => <MovieCard key={movie.id} movie={movie} />)}
        </div>
    );
}
