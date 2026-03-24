import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "CineBook - Đặt vé xem phim online",
    template: "%s | CineBook",
  },
  description:
    "Đặt vé xem phim nhanh chóng, tiện lợi tại CineBook. Chọn phim, chọn ghế, trả tiền - mọi thứ chỉ trong vài bước.",
  keywords: ["đặt vé phim", "xem phim", "rạp chiếu phim", "CineBook"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className={inter.variable}>
      <body className="min-h-screen bg-[#0a0a0f] text-white antialiased">
        <Providers>
          <Navbar />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
