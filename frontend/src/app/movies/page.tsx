"use client";

import { useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { MovieCard } from "@/components/movies/MovieCard";
import { useMovies, useGenres } from "@/hooks/useMovies";
import type { MovieFilters } from "@/services/movie.service";

const STATUS_OPTIONS = [
    { value: undefined, label: "Tất cả" },
    { value: "now_showing", label: "Đang chiếu" },
    { value: "coming_soon", label: "Sắp chiếu" },
] as const;

export default function MoviesPage() {
    const [search, setSearch] = useState("");
    const [selectedStatus, setSelectedStatus] = useState<MovieFilters["status"]>(undefined);
    const [selectedGenre, setSelectedGenre] = useState<string | undefined>(undefined);

    const filters: MovieFilters = {
        status: selectedStatus,
        genre_id: selectedGenre,
        search: search || undefined,
        size: 20,
    };

    const { data, isLoading } = useMovies(filters);
    const { data: genres } = useGenres();

    return (
        <div className="pt-24 pb-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Phim</h1>
                <p className="text-[#8888aa]">Khám phá bộ sưu tập phim phong phú của chúng tôi</p>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
                {/* Search */}
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8888aa]" />
                    <input
                        type="text"
                        placeholder="Tìm kiếm phim..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-[#8888aa] focus:outline-none focus:border-[#e50914] transition-colors text-sm"
                    />
                </div>

                {/* Status filter */}
                <div className="flex items-center gap-2 glass-card rounded-xl p-1">
                    <SlidersHorizontal className="w-4 h-4 text-[#8888aa] ml-3" />
                    {STATUS_OPTIONS.map((opt) => (
                        <button
                            key={String(opt.value)}
                            onClick={() => setSelectedStatus(opt.value)}
                            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer ${selectedStatus === opt.value
                                    ? "bg-[#e50914] text-white"
                                    : "text-[#8888aa] hover:text-white hover:bg-white/5"
                                }`}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Genre filter */}
            {genres && genres.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-8">
                    <button
                        onClick={() => setSelectedGenre(undefined)}
                        className={`px-3 py-1.5 text-xs font-medium rounded-full transition-all duration-200 cursor-pointer ${!selectedGenre ? "bg-[#e50914] text-white" : "glass-card text-[#8888aa] hover:text-white"
                            }`}
                    >
                        Tất cả thể loại
                    </button>
                    {genres.map((genre) => (
                        <button
                            key={genre.id}
                            onClick={() => setSelectedGenre(genre.id === selectedGenre ? undefined : genre.id)}
                            className={`px-3 py-1.5 text-xs font-medium rounded-full transition-all duration-200 cursor-pointer ${selectedGenre === genre.id
                                    ? "bg-[#e50914] text-white"
                                    : "glass-card text-[#8888aa] hover:text-white"
                                }`}
                        >
                            {genre.name}
                        </button>
                    ))}
                </div>
            )}

            {/* Movie grid */}
            {isLoading ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                    {Array.from({ length: 10 }).map((_, i) => (
                        <div key={i} className="glass-card rounded-2xl overflow-hidden animate-pulse">
                            <div className="aspect-[2/3] bg-white/5" />
                            <div className="p-4 space-y-2">
                                <div className="h-4 bg-white/5 rounded" />
                                <div className="h-3 bg-white/5 rounded w-2/3" />
                            </div>
                        </div>
                    ))}
                </div>
            ) : data?.items && data.items.length > 0 ? (
                <>
                    <p className="text-sm text-[#8888aa] mb-4">Tìm thấy {data.total} phim</p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        {data.items.map((movie) => (
                            <MovieCard key={movie.id} movie={movie} />
                        ))}
                    </div>
                </>
            ) : (
                <div className="text-center py-16">
                    <div className="text-5xl mb-4">🎬</div>
                    <h3 className="text-lg font-semibold text-white mb-2">Không tìm thấy phim</h3>
                    <p className="text-[#8888aa] text-sm">Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
                </div>
            )}
        </div>
    );
}
