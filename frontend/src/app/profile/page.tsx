"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CalendarDays, KeyRound, Mail, Shield, User as UserIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { formatDate } from "@/lib/utils";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/auth.store";

const schema = z
    .object({
        old_password: z.string().min(1, "Nhập mật khẩu hiện tại"),
        new_password: z
            .string()
            .min(8, "Ít nhất 8 ký tự")
            .regex(/[A-Z]/, "Cần ít nhất một chữ hoa")
            .regex(/[a-z]/, "Cần ít nhất một chữ thường")
            .regex(/[0-9]/, "Cần ít nhất một chữ số")
            .regex(/[!@#$%^&*(),.?":{}|<>]/, "Cần ít nhất một ký tự đặc biệt"),
        confirmed_new_password: z.string(),
    })
    .refine((d) => d.new_password === d.confirmed_new_password, {
        message: "Mật khẩu nhập lại không khớp",
        path: ["confirmed_new_password"],
    });

type FormData = z.infer<typeof schema>;

const ROLE_LABEL = { admin: "Quản trị viên", user: "Khách hàng" } as const;

export default function ProfilePage() {
    const router = useRouter();
    const { user, isAuthenticated } = useAuthStore();

    useEffect(() => {
        if (!isAuthenticated) router.push("/login");
    }, [isAuthenticated, router]);

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<FormData>({ resolver: zodResolver(schema) });

    if (!isAuthenticated || !user) return null;

    const onSubmit = async (data: FormData) => {
        try {
            await authService.changePassword(data);
            toast.success("Đã đổi mật khẩu");
            reset();
        } catch {
            toast.error("Không đổi được mật khẩu", {
                description: "Kiểm tra lại mật khẩu hiện tại.",
            });
        }
    };

    const facts = [
        { icon: UserIcon, label: "Tên đăng nhập", value: user.username, mono: true },
        { icon: Mail, label: "Email", value: user.email },
        { icon: CalendarDays, label: "Tham gia", value: formatDate(user.created_at) },
    ];

    return (
        <div className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-10 sm:px-6">
            <Card>
                <CardContent className="flex flex-wrap items-center gap-4">
                    <Avatar className="size-14">
                        <AvatarFallback className="bg-primary text-lg text-primary-foreground">
                            {(user.full_name || user.username).charAt(0).toUpperCase()}
                        </AvatarFallback>
                    </Avatar>
                    <div className="min-w-0 flex-1">
                        <h1 className="truncate text-xl font-semibold">
                            {user.full_name || user.username}
                        </h1>
                        <p className="truncate text-sm text-muted-foreground">{user.email}</p>
                    </div>
                    <Badge variant={user.role === "admin" ? "default" : "secondary"}>
                        <Shield className="size-3" />
                        {ROLE_LABEL[user.role]}
                    </Badge>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Thông tin tài khoản</CardTitle>
                </CardHeader>
                <CardContent>
                    <dl className="flex flex-col">
                        {facts.map(({ icon: Icon, label, value, mono }) => (
                            <div
                                key={label}
                                className="flex items-baseline justify-between gap-3 border-b py-3 last:border-b-0"
                            >
                                <dt className="flex items-center gap-1.5 text-sm text-muted-foreground">
                                    <Icon className="size-3.5" />
                                    {label}
                                </dt>
                                <dd className={mono ? "code text-sm" : "text-sm"}>{value}</dd>
                            </div>
                        ))}
                    </dl>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                        <KeyRound className="size-4" />
                        Đổi mật khẩu
                    </CardTitle>
                    <CardDescription>
                        Tối thiểu 8 ký tự, có chữ hoa, chữ thường, số và ký tự đặc biệt.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form
                        onSubmit={handleSubmit(onSubmit)}
                        className="flex flex-col gap-4"
                        noValidate
                    >
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="old-password">Mật khẩu hiện tại</Label>
                            <Input
                                id="old-password"
                                type="password"
                                autoComplete="current-password"
                                aria-invalid={!!errors.old_password}
                                {...register("old_password")}
                            />
                            {errors.old_password && (
                                <p className="text-xs text-destructive">
                                    {errors.old_password.message}
                                </p>
                            )}
                        </div>

                        <div className="flex flex-col gap-2">
                            <Label htmlFor="new-password">Mật khẩu mới</Label>
                            <Input
                                id="new-password"
                                type="password"
                                autoComplete="new-password"
                                aria-invalid={!!errors.new_password}
                                {...register("new_password")}
                            />
                            {errors.new_password && (
                                <p className="text-xs text-destructive">
                                    {errors.new_password.message}
                                </p>
                            )}
                        </div>

                        <div className="flex flex-col gap-2">
                            <Label htmlFor="confirm-new-password">Nhập lại mật khẩu mới</Label>
                            <Input
                                id="confirm-new-password"
                                type="password"
                                autoComplete="new-password"
                                aria-invalid={!!errors.confirmed_new_password}
                                {...register("confirmed_new_password")}
                            />
                            {errors.confirmed_new_password && (
                                <p className="text-xs text-destructive">
                                    {errors.confirmed_new_password.message}
                                </p>
                            )}
                        </div>

                        <Button type="submit" disabled={isSubmitting} className="mt-1 self-start">
                            {isSubmitting && <Spinner />}
                            {isSubmitting ? "Đang lưu..." : "Đổi mật khẩu"}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
