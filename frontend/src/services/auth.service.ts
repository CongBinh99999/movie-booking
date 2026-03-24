import { apiClient } from "@/lib/api";
import type { LoginCredentials, RegisterData, TokenResponse, User } from "@/types";

export const authService = {
    login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
        // FastAPI expects form data for OAuth2 password flow
        const formData = new URLSearchParams();
        formData.append("username", credentials.username);
        formData.append("password", credentials.password);

        const response = await apiClient.post<TokenResponse>("/auth/login", formData, {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
        return response.data;
    },

    register: async (data: RegisterData): Promise<User> => {
        const response = await apiClient.post<User>("/auth/register", data);
        return response.data;
    },

    getMe: async (): Promise<User> => {
        const response = await apiClient.get<User>("/auth/me");
        return response.data;
    },

    logout: () => {
        if (typeof window !== "undefined") {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
        }
    },

    changePassword: async (data: { old_password: string; new_password: string; confirmed_new_password: string }): Promise<void> => {
        await apiClient.post("/auth/me/change-password", data);
    },
};
