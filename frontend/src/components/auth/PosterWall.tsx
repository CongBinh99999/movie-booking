"use client";

import { Poster } from "@/components/movies/Poster";
import { Skeleton } from "@/components/ui/skeleton";
import { useNowShowing } from "@/hooks/useMovies";

/**
 * Mảng poster phim đang chiếu, làm nền cho cột phải của trang đăng nhập.
 *
 * Tham chiếu (claude.ai/login) dùng một tấm ảnh lớn để cột phải không rỗng.
 * Ở đây poster chính là "ảnh" sẵn có và đúng chủ đề hơn ảnh stock — đồng thời
 * cho người chưa đăng nhập thấy ngay đang có phim gì.
 */
export function PosterWall() {
    const { data, isLoading } = useNowShowing();
    const movies = data?.items.slice(0, 6);

    return (
        <div className="relative size-full overflow-hidden rounded-3xl bg-muted">
            {/* Nghiêng nhẹ và phóng to để mảng poster tràn khỏi khung, đọc như
                một bức tường chứ không phải một lưới thumbnail. */}
            <div className="absolute inset-0 scale-[1.18] -rotate-6">
                <div className="grid h-full grid-cols-3 gap-3 p-3">
                    {isLoading
                        ? Array.from({ length: 6 }, (_, i) => (
                              <Skeleton key={i} className="rounded-poster size-full" />
                          ))
                        : movies?.map((movie, i) => (
                              <div
                                  key={movie.id}
                                  className="rounded-poster relative overflow-hidden shadow-lg"
                                  style={{ transform: `translateY(${(i % 3) * 14 - 14}px)` }}
                              >
                                  <Poster
                                      src={movie.poster_url}
                                      title={movie.title}
                                      sizes="220px"
                                  />
                              </div>
                          ))}
                </div>
            </div>

            {/* Phủ một lớp tối dần về phía cột chữ để mép trái không cắt ngang
                poster một cách thô. */}
            <div className="absolute inset-0 bg-gradient-to-r from-background/70 via-background/10 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-t from-background/60 to-transparent" />
        </div>
    );
}
