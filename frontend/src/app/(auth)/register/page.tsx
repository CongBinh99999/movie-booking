"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Film, Eye, EyeOff, Loader2 } from "lucide-react";
import { authService } from "@/services/auth.service";

const registerSchema = z
    .object({
        full_name: z.string().min(2, "Tên phải có ít nhất 2 ký tự"),
        email: z.string().email("Email không hợp lệ"),
        phone_number: z.string().optional(),
        password: z.string().min(8, "Mật khẩu phải có ít nhất 8 ký tự"),
        confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "Mật khẩu xác nhận không khớp",
        path: ["confirmPassword"],
    });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const router = useRouter();
    const [showPassword, setShowPassword] = useState(false);
    const [serverError, setServerError] = useState("");

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterFormData) => {
        setServerError("");
        try {
            await authService.register({
                full_name: data.full_name,
                email: data.email,
                password: data.password,
                phone_number: data.phone_number,
            });
            router.push("/login?registered=true");
        } catch {
            setServerError("Email đã được sử dụng hoặc có lỗi xảy ra.");
        }
    };

    const fields = [
        { id: "full_name", label: "Họ và tên", type: "text", placeholder: "Nguyễn Văn A", autoComplete: "name" },
        { id: "email", label: "Email", type: "email", placeholder: "email@example.com", autoComplete: "email" },
        { id: "phone_number", label: "Số điện thoại (tùy chọn)", type: "tel", placeholder: "0912345678", autoComplete: "tel" },
    ] as const;

    return (
        <div className="min-h-screen pt-16 flex items-center justify-center px-4 py-8">
            <div className="w-full max-w-md animate-fade-in">
                <div className="glass-card rounded-2xl p-8">
                    <div className="text-center mb-8">
                        <div className="inline-flex p-3 bg-[#e50914]/10 rounded-xl mb-4">
                            <Film className="w-7 h-7 text-[#e50914]" />
                        </div>
                        <h1 className="text-2xl font-bold text-white">Tạo tài khoản</h1>
                        <p className="text-[#8888aa] mt-1 text-sm">Tham gia CineBook để đặt vé dễ dàng</p>
                    </div>

                    {serverError && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg">
                            {serverError}
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {fields.map((field) => (
                            <div key={field.id}>
                                <label htmlFor={field.id} className="block text-sm font-medium text-[#8888aa] mb-1.5">
                                    {field.label}
                                </label>
                                <input
                                    id={field.id}
                                    type={field.type}
                                    placeholder={field.placeholder}
                                    autoComplete={field.autoComplete}
                                    {...register(field.id)}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-[#8888aa] focus:outline-none focus:border-[#e50914] transition-colors text-sm"
                                />
                                {errors[field.id]?.message && (
                                    <p className="text-red-400 text-xs mt-1">{errors[field.id]?.message}</p>
                                )}
                            </div>
                        ))}

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-[#8888aa] mb-1.5">
                                Mật khẩu
                            </label>
                            <div className="relative">
                                <input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    autoComplete="new-password"
                                    {...register("password")}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-[#8888aa] focus:outline-none focus:border-[#e50914] transition-colors text-sm pr-10"
                                />
                                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8888aa] hover:text-white transition-colors cursor-pointer" aria-label="Toggle password visibility">
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>}
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-[#8888aa] mb-1.5">
                                Xác nhận mật khẩu
                            </label>
                            <input
                                id="confirmPassword"
                                type="password"
                                placeholder="••••••••"
                                autoComplete="new-password"
                                {...register("confirmPassword")}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-[#8888aa] focus:outline-none focus:border-[#e50914] transition-colors text-sm"
                            />
                            {errors.confirmPassword && <p className="text-red-400 text-xs mt-1">{errors.confirmPassword.message}</p>}
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full flex items-center justify-center gap-2 py-3 bg-[#e50914] hover:bg-[#b20710] disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors duration-200 cursor-pointer"
                        >
                            {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                            Đăng ký
                        </button>
                    </form>

                    <p className="text-center text-sm text-[#8888aa] mt-6">
                        Đã có tài khoản?{" "}
                        <Link href="/login" className="text-[#e50914] hover:text-[#b20710] font-medium transition-colors">
                            Đăng nhập
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
