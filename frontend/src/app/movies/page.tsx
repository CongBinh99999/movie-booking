"use client";

import { Film, Search, X } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense, useDeferredValue, useState } from "react";

import { MovieGrid } from "@/components/movies/MovieCard";
import { Button } from "@/components/ui/button";
import {
    Empty,
    EmptyDescription,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
} from "@/components/ui/empty";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { useMovies } from "@/hooks/useMovies";
import type { MovieFilters } from "@/services/movie.service";

const STATUS_OPTIONS = [
    { value: "all", label: "Tất cả" },
    { value: "now_showing", label: "Đang chiếu" },
    { value: "coming_soon", label: "Sắp chiếu" },
    { value: "ended", label: "Đã kết thúc" },
] as const;

type StatusValue = (typeof STATUS_OPTIONS)[number]["value"];

function MoviesBrowser() {
    const searchParams = useSearchParams();
    const [title, setTitle] = useState("");

    // /movies?status=coming_soon (từ footer) quyết định giá trị ban đầu; khi
    // người dùng tự chọn thì lựa chọn đó thắng. Suy trực tiếp, không cần effect
    // đồng bộ — effect kiểu đó gây thêm một vòng render.
    const fromUrl = searchParams.get("status");
    const urlStatus: StatusValue = STATUS_OPTIONS.some((o) => o.value === fromUrl)
        ? (fromUrl as StatusValue)
        : "all";
    const [picked, setPicked] = useState<StatusValue | null>(null);
    const status = picked ?? urlStatus;
    const setStatus = setPicked;

    // Gõ tới đâu lọc tới đó, nhưng không chặn ô nhập khi danh sách đang render.
    const deferredTitle = useDeferredValue(title);

    const filters: MovieFilters = {
        limit: 40,
        ...(status !== "all" && { status }),
        ...(deferredTitle.trim() && { title: deferredTitle.trim() }),
    };

    const { data, isLoading, isError } = useMovies(filters);
    const movies = data?.items;
    const hasFilter = status !== "all" || title.trim().length > 0;

    return (
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
            <h1 className="text-3xl sm:text-4xl">Phim</h1>
            <p className="mt-1 text-muted-foreground">
                {data ? `${data.total} phim` : "Đang tải danh sách phim"}
            </p>

            <div className="mt-6 mb-6 flex flex-col gap-2.5 sm:flex-row">
                <div className="relative flex-1">
                    <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                        id="movie-search"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Tìm theo tên phim"
                        className="pl-9"
                        aria-label="Tìm theo tên phim"
                    />
                    {title && (
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setTitle("")}
                            className="absolute top-1/2 right-1 size-7 -translate-y-1/2"
                            aria-label="Xoá từ khoá"
                        >
                            <X className="size-3.5" />
                        </Button>
                    )}
                </div>

                <Select value={status} onValueChange={(v) => setStatus(v as StatusValue)}>
                    <SelectTrigger className="sm:w-44" aria-label="Lọc theo trạng thái">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        {STATUS_OPTIONS.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                                {option.label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            {isError ? (
                <Empty className="border">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Film />
                        </EmptyMedia>
                        <EmptyTitle>Không tải được danh sách phim</EmptyTitle>
                        <EmptyDescription>
                            Kiểm tra kết nối rồi tải lại trang.
                        </EmptyDescription>
                    </EmptyHeader>
                </Empty>
            ) : !isLoading && !movies?.length ? (
                <Empty className="border">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Film />
                        </EmptyMedia>
                        <EmptyTitle>Không có phim nào khớp</EmptyTitle>
                        <EmptyDescription>
                            {hasFilter
                                ? "Thử bỏ bớt bộ lọc hoặc đổi từ khoá."
                                : "Danh sách phim đang trống."}
                        </EmptyDescription>
                    </EmptyHeader>
                    {hasFilter && (
                        <Button
                            variant="outline"
                            onClick={() => {
                                setStatus("all");
                                setTitle("");
                            }}
                        >
                            Xoá bộ lọc
                        </Button>
                    )}
                </Empty>
            ) : (
                <MovieGrid movies={movies} isLoading={isLoading} skeletonCount={10} />
            )}
        </div>
    );
}

export default function MoviesPage() {
    return (
        <Suspense fallback={null}>
            <MoviesBrowser />
        </Suspense>
    );
}
