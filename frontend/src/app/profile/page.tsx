"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { User, Lock, Eye, EyeOff, Loader2, CheckCircle, Shield, Calendar } from "lucide-react";
import { useAuthStore } from "@/store/auth.store";
import { authService } from "@/services/auth.service";
import { formatDate } from "@/lib/utils";

const changePasswordSchema = z
    .object({
        old_password: z.string().min(1, "Vui lòng nhập mật khẩu hiện tại"),
        new_password: z
            .string()
            .min(8, "Mật khẩu mới phải có ít nhất 8 ký tự")
            .regex(/[A-Z]/, "Phải chứa ít nhất một chữ hoa")
            .regex(/[a-z]/, "Phải chứa ít nhất một chữ thường")
            .regex(/[0-9]/, "Phải chứa ít nhất một số")
            .regex(/[!@#$%^&*(),.?":{}|<>]/, "Phải chứa ít nhất một ký tự đặc biệt"),
        confirmed_new_password: z.string(),
    })
    .refine((data) => data.new_password === data.confirmed_new_password, {
        message: "Mật khẩu xác nhận không khớp",
        path: ["confirmed_new_password"],
    });

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

export default function ProfilePage() {
    const router = useRouter();
    const { user, isAuthenticated } = useAuthStore();
    const [showOldPassword, setShowOldPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [passwordError, setPasswordError] = useState("");
    const [passwordSuccess, setPasswordSuccess] = useState(false);

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<ChangePasswordFormData>({
        resolver: zodResolver(changePasswordSchema),
    });

    useEffect(() => {
        if (!isAuthenticated || !user) {
            router.push("/login");
        }
    }, [isAuthenticated, user, router]);

    if (!isAuthenticated || !user) {
        return null;
    }

    const onSubmitPassword = async (data: ChangePasswordFormData) => {
        setPasswordError("");
        setPasswordSuccess(false);
        try {
            await authService.changePassword({
                old_password: data.old_password,
                new_password: data.new_password,
                confirmed_new_password: data.confirmed_new_password,
            });
            setPasswordSuccess(true);
            reset();
        } catch {
            setPasswordError("Mật khẩu hiện tại không chính xác hoặc có lỗi xảy ra.");
        }
    };

    return (
        <div className="pt-16 pb-12 min-h-screen">
            <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <div className="w-16 h-16 rounded-full bg-[#e50914] flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-[#e50914]/20">
                        {user.full_name?.charAt(0)?.toUpperCase() || "U"}
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">{user.full_name || "Người dùng"}</h1>
                        <p className="text-[#8888aa] text-sm">{user.email}</p>
                    </div>
                </div>

                {/* Profile Info */}
                <div className="glass-card rounded-2xl p-6 mb-6">
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <User className="w-5 h-5 text-[#e50914]" />
                        Thông tin cá nhân
                    </h2>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between py-3 border-b border-white/5">
                            <span className="text-[#8888aa] text-sm">Họ và tên</span>
                            <span className="text-white text-sm font-medium">{user.full_name || "Chưa cập nhật"}</span>
                        </div>
                        <div className="flex items-center justify-between py-3 border-b border-white/5">
                            <span className="text-[#8888aa] text-sm">Email</span>
                            <span className="text-white text-sm font-medium">{user.email}</span>
                        </div>
                        <div className="flex items-center justify-between py-3 border-b border-white/5">
                            <span className="text-[#8888aa] text-sm flex items-center gap-1.5">
                                <Shield className="w-3.5 h-3.5" /> Vai trò
                            </span>
                            <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${user.role === "admin" ? "bg-purple-500/15 text-purple-400" : "bg-blue-500/15 text-blue-400"}`}>
                                {user.role === "admin" ? "Quản trị viên" : "Khách hàng"}
                            </span>
                        </div>
                        <div className="flex items-center justify-between py-3 border-b border-white/5">
                            <span className="text-[#8888aa] text-sm">Trạng thái</span>
                            <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${user.is_active ? "bg-green-500/15 text-green-400" : "bg-red-500/15 text-red-400"}`}>
                                {user.is_active ? "Đang hoạt động" : "Đã vô hiệu hóa"}
                            </span>
                        </div>
                        <div className="flex items-center justify-between py-3">
                            <span className="text-[#8888aa] text-sm flex items-center gap-1.5">
                                <Calendar className="w-3.5 h-3.5" /> Ngày tham gia
                            </span>
                            <span className="text-white text-sm font-medium">{formatDate(user.created_at)}</span>
                        </div>
                    </div>
                </div>

                {/* Change Password */}
                <div className="glass-card rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Lock className="w-5 h-5 text-[#e50914]" />
                        Đổi mật khẩu
                    </h2>

                    {passwordSuccess && (
                        <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 text-green-400 text-sm rounded-lg flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 shrink-0" />
                            Đổi mật khẩu thành công!
                        </div>
                    )}
                    {passwordError && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg">
                            {passwordError}
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmitPassword)} className="space-y-4">
                        {/* Old password */}
                        <div>
                            <label htmlFor="old_password" className="block text-sm font-medium text-[#8888aa] mb-1.5">
                                Mật khẩu hiện tại
                            </label>
                            <div className="relative">
                                <input
                                    id="old_password"
                                    type={showOldPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    autoComplete="current-password"
                                    {...register("old_password")}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-[#8888aa] focus:outline-none focus:border-[#e50914] transition-colors text-sm pr-10"
                                />
                                <button type="button" onClick={() => setShowOldPassword(!showOldPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8888aa] hover:text-white transition-colors cursor-pointer" aria-label="Toggle password">
                                    {showOldPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            {errors.old_password && <p className="text-red-400 text-xs mt-1">{errors.old_password.message}</p>}
                        </div>

                        {/* New password */}
                        <div>
                            <label htmlFor="new_password" className="block text-sm font-medium text-[#8888aa] mb-1.5">
                                Mật khẩu mới
                            </label>
                            <div className="relative">
                                <input
                                    id="new_password"
                                    type={showNewPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    autoComplete="new-password"
                                    {...register("new_password")}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-[#8888aa] focus:outline-none focus:border-[#e50914] transition-colors text-sm pr-10"
                                />
                                <button type="button" onClick={() => setShowNewPassword(!showNewPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8888aa] hover:text-white transition-colors cursor-pointer" aria-label="Toggle password">
                                    {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            {errors.new_password && <p className="text-red-400 text-xs mt-1">{errors.new_password.message}</p>}
                        </div>

                        {/* Confirm new password */}
                        <div>
                            <label htmlFor="confirmed_new_password" className="block text-sm font-medium text-[#8888aa] mb-1.5">
                                Xác nhận mật khẩu mới
                            </label>
                            <input
                                id="confirmed_new_password"
                                type="password"
                                placeholder="••••••••"
                                autoComplete="new-password"
                                {...register("confirmed_new_password")}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-[#8888aa] focus:outline-none focus:border-[#e50914] transition-colors text-sm"
                            />
                            {errors.confirmed_new_password && <p className="text-red-400 text-xs mt-1">{errors.confirmed_new_password.message}</p>}
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full flex items-center justify-center gap-2 py-3 bg-[#e50914] hover:bg-[#b20710] disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors duration-200 cursor-pointer"
                        >
                            {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                            Đổi mật khẩu
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
