import Image from "next/image";
import Link from "next/link";
import { Clock, Star } from "lucide-react";
import type { Movie } from "@/types";

const STATUS_LABELS: Record<Movie["status"], { label: string; color: string }> = {
    now_showing: { label: "Đang chiếu", color: "bg-green-500" },
    coming_soon: { label: "Sắp chiếu", color: "bg-blue-500" },
    ended: { label: "Đã kết thúc", color: "bg-gray-500" },
};

interface MovieCardProps {
    movie: Movie;
}

export function MovieCard({ movie }: MovieCardProps) {
    const statusInfo = STATUS_LABELS[movie.status];

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
                {/* Rating */}
                {movie.rating && (
                    <div className="absolute top-3 right-3 flex items-center gap-1 bg-black/60 backdrop-blur-sm px-2 py-1 rounded-full">
                        <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                        <span className="text-xs font-semibold text-white">{movie.rating.toFixed(1)}</span>
                    </div>
                )}
            </div>

            {/* Info */}
            <div className="p-4">
                <h3 className="font-semibold text-white text-sm leading-tight mb-1 line-clamp-2 group-hover:text-[#e50914] transition-colors duration-200">
                    {movie.title}
                </h3>
                <div className="flex items-center gap-1 text-[#8888aa]">
                    <Clock className="w-3 h-3" />
                    <span className="text-xs">{movie.duration} phút</span>
                </div>
                {movie.genres.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                        {movie.genres.slice(0, 2).map((genre) => (
                            <span
                                key={genre.id}
                                className="text-xs px-2 py-0.5 bg-white/5 text-[#8888aa] rounded-full"
                            >
                                {genre.name}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </Link>
    );
}
