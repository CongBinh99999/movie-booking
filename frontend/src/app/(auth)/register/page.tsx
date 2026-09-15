"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { AlertCircle, Eye, EyeOff } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { FieldRow } from "@/components/ui/field-row";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { authService } from "@/services/auth.service";

// Khớp đúng validator của RegisterRequest phía backend, để lỗi hiện ngay tại
// form thay vì phải chờ một vòng 422.
const schema = z
    .object({
        username: z
            .string()
            .min(3, "Ít nhất 3 ký tự")
            .max(100, "Tối đa 100 ký tự")
            .regex(
                /^[a-zA-Z][a-zA-Z0-9_]*$/,
                "Bắt đầu bằng chữ cái, chỉ gồm chữ, số và gạch dưới"
            ),
        email: z.string().email("Email không hợp lệ"),
        full_name: z
            .string()
            .min(5, "Ít nhất 5 ký tự")
            .max(255, "Tối đa 255 ký tự")
            .optional()
            .or(z.literal("")),
        password: z
            .string()
            .min(8, "Ít nhất 8 ký tự")
            .regex(/[A-Z]/, "Cần ít nhất một chữ hoa")
            .regex(/[a-z]/, "Cần ít nhất một chữ thường")
            .regex(/[0-9]/, "Cần ít nhất một chữ số")
            .regex(/[!@#$%^&*(),.?":{}|<>]/, "Cần ít nhất một ký tự đặc biệt"),
        confirmed_password: z.string(),
    })
    .refine((data) => data.password === data.confirmed_password, {
        message: "Mật khẩu nhập lại không khớp",
        path: ["confirmed_password"],
    });

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
    const router = useRouter();
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
            await authService.register({
                username: data.username,
                email: data.email,
                password: data.password,
                confirmed_password: data.confirmed_password,
                ...(data.full_name && { full_name: data.full_name }),
            });
            toast.success("Tạo tài khoản thành công", {
                description: "Đăng nhập để bắt đầu đặt vé.",
            });
            router.push("/login");
        } catch {
            setServerError("Email hoặc tên đăng nhập đã được dùng.");
        }
    };

    return (
        <div className="flex flex-col gap-7">
            <div className="flex flex-col gap-2 text-center">
                <h1 className="text-4xl sm:text-[2.75rem]">Tạo tài khoản</h1>
                <p className="text-muted-foreground">Đặt vé nhanh hơn ở những lần sau</p>
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
                        id="reg-username"
                        label="Tên đăng nhập"
                        error={errors.username?.message}
                    >
                        <Input
                            id="reg-username"
                            autoComplete="username"
                            aria-invalid={!!errors.username}
                            className="h-11"
                            {...register("username")}
                        />
                    </FieldRow>

                    <FieldRow id="reg-email" label="Email" error={errors.email?.message}>
                        <Input
                            id="reg-email"
                            type="email"
                            autoComplete="email"
                            aria-invalid={!!errors.email}
                            className="h-11"
                            {...register("email")}
                        />
                    </FieldRow>

                    <FieldRow
                        id="reg-fullname"
                        label="Họ và tên"
                        hint="Không bắt buộc"
                        error={errors.full_name?.message}
                    >
                        <Input
                            id="reg-fullname"
                            autoComplete="name"
                            aria-invalid={!!errors.full_name}
                            className="h-11"
                            {...register("full_name")}
                        />
                    </FieldRow>

                    <FieldRow
                        id="reg-password"
                        label="Mật khẩu"
                        hint="Tối thiểu 8 ký tự, có chữ hoa, chữ thường, số và ký tự đặc biệt"
                        error={errors.password?.message}
                    >
                        <div className="relative">
                            <Input
                                id="reg-password"
                                type={showPassword ? "text" : "password"}
                                autoComplete="new-password"
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

                    <FieldRow
                        id="reg-confirm"
                        label="Nhập lại mật khẩu"
                        error={errors.confirmed_password?.message}
                    >
                        <Input
                            id="reg-confirm"
                            type={showPassword ? "text" : "password"}
                            autoComplete="new-password"
                            aria-invalid={!!errors.confirmed_password}
                            className="h-11"
                            {...register("confirmed_password")}
                        />
                    </FieldRow>

                    <Button
                        type="submit"
                        disabled={isSubmitting}
                        className="mt-2 h-11 w-full text-[0.9375rem]"
                    >
                        {isSubmitting && <Spinner />}
                        {isSubmitting ? "Đang tạo tài khoản..." : "Đăng ký"}
                    </Button>
                </form>
            </div>

            <p className="text-center text-sm text-muted-foreground">
                Đã có tài khoản?
                <Link
                    href="/login"
                    className="ml-1 font-medium text-brand underline-offset-4 hover:underline"
                >
                    Đăng nhập
                </Link>
            </p>
        </div>
    );
}
