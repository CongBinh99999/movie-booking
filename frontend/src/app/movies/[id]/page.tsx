"use client";

import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Clock, Star, Calendar, ChevronRight, Play } from "lucide-react";
import { useMovie } from "@/hooks/useMovies";
import { useShowtimesByMovie } from "@/hooks/useShowtimes";
import { formatDate, formatTime } from "@/lib/utils";

export default function MovieDetailPage() {
    const { id } = useParams<{ id: string }>();
    const { data: movie, isLoading: isLoadingMovie } = useMovie(id);
    const { data: showtimes, isLoading: isLoadingShowtimes } = useShowtimesByMovie(id);

    if (isLoadingMovie) {
        return (
            <div className="pt-16 min-h-screen">
                <div className="max-w-7xl mx-auto px-4 py-12 animate-pulse">
                    <div className="flex flex-col md:flex-row gap-8">
                        <div className="w-full md:w-72 aspect-[2/3] bg-white/5 rounded-2xl" />
                        <div className="flex-1 space-y-4">
                            <div className="h-8 bg-white/5 rounded w-3/4" />
                            <div className="h-4 bg-white/5 rounded w-1/2" />
                            <div className="h-24 bg-white/5 rounded" />
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!movie) {
        return (
            <div className="pt-24 text-center">
                <h2 className="text-xl text-white">Không tìm thấy phim</h2>
                <Link href="/movies" className="text-[#e50914] hover:underline mt-2 inline-block">
                    Quay lại danh sách phim
                </Link>
            </div>
        );
    }

    return (
        <div className="pt-16 pb-12">
            {/* Hero backdrop */}
            <div className="relative w-full h-72 md:h-96 overflow-hidden">
                {movie.poster_url && (
                    <Image src={movie.poster_url} alt={movie.title} fill className="object-cover blur-sm brightness-40 scale-105" />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-[#0a0a0f]/60 to-transparent" />
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-48 relative z-10 animate-fade-in">
                <div className="flex flex-col md:flex-row gap-8">
                    {/* Poster */}
                    <div className="w-44 md:w-64 shrink-0 mx-auto md:mx-0">
                        <div className="relative aspect-[2/3] rounded-2xl overflow-hidden shadow-2xl glass-card border border-white/10">
                            {movie.poster_url ? (
                                <Image src={movie.poster_url} alt={movie.title} fill className="object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-4xl">🎬</div>
                            )}
                        </div>
                        {movie.trailer_url && (
                            <a
                                href={movie.trailer_url}
                                target="_blank"
                                rel="noreferrer"
                                className="mt-3 flex items-center justify-center gap-2 w-full py-2.5 glass-card hover:bg-white/10 text-white text-sm font-medium rounded-xl transition-all duration-200 cursor-pointer"
                            >
                                <Play className="w-4 h-4 text-[#e50914] fill-[#e50914]" /> Xem trailer
                            </a>
                        )}
                    </div>

                    {/* Info */}
                    <div className="flex-1 pt-8 md:pt-16">
                        <div className="flex flex-wrap gap-2 mb-3">
                            {movie.genres?.map((g) => (
                                <span key={g.id} className="text-xs px-2.5 py-1 bg-[#e50914]/15 text-[#e50914] rounded-full font-medium">
                                    {g.name}
                                </span>
                            ))}
                        </div>
                        <h1 className="text-3xl md:text-4xl font-extrabold text-white mb-3">{movie.title}</h1>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-[#8888aa] mb-5">
                            {movie.rating && (
                                <span className="flex items-center gap-1 text-yellow-400 font-semibold">
                                    <Star className="w-4 h-4 fill-yellow-400" /> {movie.rating.toFixed(1)}/10
                                </span>
                            )}
                            <span className="flex items-center gap-1">
                                <Clock className="w-4 h-4" /> {movie.duration} phút
                            </span>
                            <span className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" /> {formatDate(movie.release_date)}
                            </span>
                        </div>
                        <p className="text-[#8888aa] leading-relaxed mb-8 max-w-2xl">{movie.description}</p>

                        {/* Showtimes */}
                        <div>
                            <h2 className="text-xl font-bold text-white mb-4">Lịch chiếu</h2>
                            {isLoadingShowtimes ? (
                                <div className="space-y-2">
                                    {[1, 2, 3].map((i) => (
                                        <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />
                                    ))}
                                </div>
                            ) : showtimes && showtimes.length > 0 ? (
                                <div className="space-y-3">
                                    {showtimes.map((showtime) => (
                                        <Link
                                            key={showtime.id}
                                            href={`/booking/${showtime.id}`}
                                            className="flex items-center justify-between p-4 glass-card rounded-xl hover:bg-white/10 hover:border-white/20 transition-all duration-200 group cursor-pointer"
                                        >
                                            <div>
                                                <div className="text-white font-semibold">
                                                    {formatTime(showtime.start_time)} - {formatTime(showtime.end_time)}
                                                </div>
                                                <div className="text-xs text-[#8888aa] mt-0.5">{formatDate(showtime.start_time)}</div>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <span className="text-[#e50914] font-semibold text-sm">
                                                    {new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(showtime.price)}
                                                </span>
                                                <ChevronRight className="w-4 h-4 text-[#8888aa] group-hover:text-white transition-colors" />
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-[#8888aa] text-sm">Chưa có lịch chiếu cho phim này.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
