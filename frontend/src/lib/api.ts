import axios from "axios";
import { useAuthStore } from "@/store/auth.store";

// Mọi router backend đều mount dưới /api/v1 (xem app/main.py).
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const apiClient = axios.create({
    baseURL: BASE_URL,
});

apiClient.interceptors.request.use((config) => {
    const token = useAuthStore.getState().token;
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        // Access token sống 15 phút. Hết hạn mà không dọn thì user kẹt ở
        // trạng thái nửa đăng nhập: store bảo đã login, mọi request đều 401.
        const isExpiredSession =
            error.response?.status === 401 && useAuthStore.getState().isAuthenticated;

        if (isExpiredSession) {
            useAuthStore.getState().clearAuth();
            if (typeof window !== "undefined") {
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);
