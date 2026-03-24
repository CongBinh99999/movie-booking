import type { NextConfig } from "next";

// Bỏ qua lỗi SSL certificate tự ký khi chạy môi trường dev cục bộ
// (UNABLE_TO_GET_ISSUER_CERT_LOCALLY).
// KHÔNG bật trên production — chỉ áp dụng khi NODE_ENV !== "production".
if (process.env.NODE_ENV !== "production") {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
}

const nextConfig: NextConfig = {
  images: {
    // Cho phép tải ảnh từ mọi domain HTTPS (wildcard).
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
      // Bổ sung HTTP cho ảnh nội bộ / localhost khi dev
      {
        protocol: "http",
        hostname: "**",
      },
    ],
    // Tắt tối ưu hoá ảnh phía server để tránh Next.js
    // tự fetch lại qua SSL proxy — ảnh hiển thị nguyên gốc từ src URL.
    unoptimized: true,
  },
};

export default nextConfig;
