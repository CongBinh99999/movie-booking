import Image from "next/image";
import Link from "next/link";
import { Clock } from "lucide-react";
import { getMovieStatus, type Movie, type MovieStatus } from "@/types";

// MovieResponse không có trường `status`; suy ra từ is_active + release_date
// + end_date (xem getMovieStatus). Cũng không kèm `genres` và `rating`.
const STATUS_LABELS: Record<MovieStatus, { label: string; color: string }> = {
    now_showing: { label: "Đang chiếu", color: "bg-green-500" },
    coming_soon: { label: "Sắp chiếu", color: "bg-blue-500" },
    ended: { label: "Đã kết thúc", color: "bg-gray-500" },
};

interface MovieCardProps {
    movie: Movie;
}

export function MovieCard({ movie }: MovieCardProps) {
    const statusInfo = STATUS_LABELS[getMovieStatus(movie)];

    return (
        <Link
            href={`/movies/${movie.id}`}
            className="group block relative glass-card rounded-2xl overflow-hidden hover:border-white/20 transition-all duration-300 cursor-pointer"
        >
            {/* Poster */}
            <div className="relative aspect-[2/3] overflow-hidden bg-[#1e1e2e]">
                {movie.poster_url ? (
                    <Image
                        src={movie.poster_url}
                        alt={movie.title}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center">
                        <span className="text-[#8888aa] text-4xl">🎬</span>
                    </div>
                )}
                {/* Overlay on hover */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                {/* Status badge */}
                <div className="absolute top-3 left-3">
                    <span className={`px-2 py-1 text-xs font-semibold text-white rounded-full ${statusInfo.color}`}>
                        {statusInfo.label}
                    </span>
                </div>
            </div>

            {/* Info */}
            <div className="p-4">
                <h3 className="font-semibold text-white text-sm leading-tight mb-1 line-clamp-2 group-hover:text-[#e50914] transition-colors duration-200">
                    {movie.title}
                </h3>
                <div className="flex items-center gap-1 text-[#8888aa]">
                    <Clock className="w-3 h-3" />
                    <span className="text-xs">{movie.duration_minutes} phút</span>
                </div>
            </div>
        </Link>
    );
}
