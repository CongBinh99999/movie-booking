"use client";

import Link from "next/link";
import { ArrowRight, ChevronRight, Film, Popcorn, Ticket } from "lucide-react";
import { MovieCard } from "@/components/movies/MovieCard";
import { useNowShowing, useComingSoon } from "@/hooks/useMovies";

function HeroSection() {
  return (
    <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#1a0a14] via-[#0a0a0f] to-[#0a0a1a]" />
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#e50914]/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-purple-900/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto text-center px-4 animate-fade-in">
        <div className="inline-flex items-center gap-2 bg-[#e50914]/10 border border-[#e50914]/20 text-[#e50914] px-4 py-2 rounded-full text-sm font-medium mb-6">
          <Popcorn className="w-4 h-4" />
          Trải nghiệm điện ảnh đỉnh cao
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-tight mb-6">
          Đặt vé{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#e50914] to-pink-500">
            thông minh
          </span>
          <br />
          xem phim dễ dàng
        </h1>
        <p className="text-lg text-[#8888aa] max-w-2xl mx-auto mb-10 leading-relaxed">
          Chọn phim yêu thích, chọn ghế ngồi, thanh toán nhanh chóng. Tất cả
          chỉ trong vài bước đơn giản tại CineBook.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
          <Link
            href="/movies"
            className="inline-flex items-center gap-2 px-8 py-4 bg-[#e50914] hover:bg-[#b20710] text-white font-semibold rounded-xl transition-all duration-200 glow-primary"
          >
            Xem phim ngay <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/movies?status=coming_soon"
            className="inline-flex items-center gap-2 px-8 py-4 glass-card hover:bg-white/10 text-white font-semibold rounded-xl transition-all duration-200"
          >
            Phim sắp chiếu <ChevronRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  );
}

function StatsSection() {
  const stats = [
    { icon: Film, value: "500+", label: "Bộ phim" },
    { icon: Ticket, value: "50+", label: "Rạp chiếu phim" },
    { icon: Popcorn, value: "1M+", label: "Vé đã bán" },
  ];

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
      <div className="grid grid-cols-3 gap-4">
        {stats.map(({ icon: Icon, value, label }) => (
          <div key={label} className="glass-card rounded-2xl p-6 text-center">
            <Icon className="w-6 h-6 text-[#e50914] mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{value}</div>
            <div className="text-sm text-[#8888aa]">{label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function MovieSection({ title, href, movies }: { title: string; href: string; movies: ReturnType<typeof useNowShowing>["data"] }) {
  if (!movies?.items?.length) return null;

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        <Link
          href={href}
          className="flex items-center gap-1 text-sm text-[#e50914] hover:text-[#b20710] transition-colors"
        >
          Xem tất cả <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {movies.items.slice(0, 10).map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </div>
    </section>
  );
}

function MovieSectionSkeleton({ title }: { title: string }) {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-2xl font-bold text-white mb-6">{title}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="glass-card rounded-2xl overflow-hidden animate-pulse">
            <div className="aspect-[2/3] bg-white/5" />
            <div className="p-4 space-y-2">
              <div className="h-4 bg-white/5 rounded" />
              <div className="h-3 bg-white/5 rounded w-2/3" />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function HomePage() {
  const { data: nowShowing, isLoading: isLoadingNow } = useNowShowing();
  const { data: comingSoon, isLoading: isLoadingComing } = useComingSoon();

  return (
    <div className="pt-16">
      <HeroSection />
      <StatsSection />

      {isLoadingNow ? (
        <MovieSectionSkeleton title="🎬 Phim đang chiếu" />
      ) : (
        <MovieSection
          title="🎬 Phim đang chiếu"
          href="/movies?status=now_showing"
          movies={nowShowing}
        />
      )}

      {isLoadingComing ? (
        <MovieSectionSkeleton title="🔜 Phim sắp chiếu" />
      ) : (
        <MovieSection
          title="🔜 Phim sắp chiếu"
          href="/movies?status=coming_soon"
          movies={comingSoon}
        />
      )}
    </div>
  );
}
