"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { AlertCircle, Eye, EyeOff } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { FieldRow } from "@/components/ui/field-row";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/auth.store";

const schema = z.object({
    username: z.string().min(3, "Tên đăng nhập phải có ít nhất 3 ký tự"),
    password: z.string().min(1, "Nhập mật khẩu"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
    const router = useRouter();
    const { setAuth } = useAuthStore();
    const [showPassword, setShowPassword] = useState(false);
    const [serverError, setServerError] = useState("");

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<FormData>({ resolver: zodResolver(schema) });

    const onSubmit = async (data: FormData) => {
        setServerError("");
        try {
            const tokens = await authService.login(data);
            // Truyền token thẳng vào getMe: store chưa có token nên interceptor
            // chưa gắn được header Authorization.
            const user = await authService.getMe(tokens.access_token);
            setAuth(user, tokens.access_token);
            router.push("/");
        } catch {
            setServerError("Tên đăng nhập hoặc mật khẩu không đúng.");
        }
    };

    return (
        <div className="flex flex-col gap-7">
            {/* Tiêu đề nằm NGOÀI card, cỡ lớn — card chỉ chứa việc phải làm. */}
            <div className="flex flex-col gap-2 text-center">
                <h1 className="text-4xl sm:text-[2.75rem]">Chào mừng trở lại</h1>
                <p className="text-muted-foreground">Đăng nhập để tiếp tục đặt vé</p>
            </div>

            <div className="surface-soft p-6 sm:p-7">
                <form
                    onSubmit={handleSubmit(onSubmit)}
                    className="flex flex-col gap-4"
                    noValidate
                >
                    {serverError && (
                        <Alert variant="destructive">
                            <AlertCircle />
                            <AlertDescription>{serverError}</AlertDescription>
                        </Alert>
                    )}

                    <FieldRow
                        id="login-username"
                        label="Tên đăng nhập"
                        error={errors.username?.message}
                    >
                        <Input
                            id="login-username"
                            autoComplete="username"
                            aria-invalid={!!errors.username}
                            className="h-11"
                            {...register("username")}
                        />
                    </FieldRow>

                    <FieldRow
                        id="login-password"
                        label="Mật khẩu"
                        error={errors.password?.message}
                    >
                        <div className="relative">
                            <Input
                                id="login-password"
                                type={showPassword ? "text" : "password"}
                                autoComplete="current-password"
                                aria-invalid={!!errors.password}
                                className="h-11 pr-11"
                                {...register("password")}
                            />
                            <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                onClick={() => setShowPassword((v) => !v)}
                                className="absolute top-1/2 right-1.5 size-8 -translate-y-1/2"
                                aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                            >
                                {showPassword ? (
                                    <EyeOff className="size-4" />
                                ) : (
                                    <Eye className="size-4" />
                                )}
                            </Button>
                        </div>
                    </FieldRow>

                    <Button
                        type="submit"
                        disabled={isSubmitting}
                        className="mt-2 h-11 w-full text-[0.9375rem]"
                    >
                        {isSubmitting && <Spinner />}
                        {isSubmitting ? "Đang đăng nhập..." : "Đăng nhập"}
                    </Button>
                </form>
            </div>

            <p className="text-center text-sm text-muted-foreground">
                Chưa có tài khoản?
                <Link
                    href="/register"
                    className="ml-1 font-medium text-brand underline-offset-4 hover:underline"
                >
                    Đăng ký
                </Link>
            </p>
        </div>
    );
}
