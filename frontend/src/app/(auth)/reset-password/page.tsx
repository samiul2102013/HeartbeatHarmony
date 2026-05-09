"use client";

import { useAppForm } from "@/components/form/form-context";
import { resetPassword } from "@/lib/index";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { z } from "zod";

const resetSchema = z
    .object({
        password: z.string().min(6, "Password must be at least 6 characters").max(32, "Password must be at most 32 characters"),
        confirmPassword: z.string().min(1, "Please confirm your password"),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "Passwords don't match",
        path: ["confirmPassword"],
    });

export default function ResetPassword() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const token = searchParams.get("token");

    const form = useAppForm({
        defaultValues: { password: "", confirmPassword: "" },
        validators: { onChange: resetSchema },
        onSubmit: async ({ value }) => {
            if (!token) {
                throw new Error("Invalid reset link");
            }
            await resetPassword(token, value.password);
            router.push("/signin");
        },
    });

    return (
        <div className="my-20 mx-auto flex w-full max-w-150 flex-col gap-6 rounded-lg border px-6 py-12">
            <div>
                <h2 className="text-center text-2xl font-bold">Reset Password</h2>
                <p className="mt-2 text-center text-muted-foreground">Create a new password for your account.</p>
            </div>

            <form
                className="grid gap-6"
                onSubmit={(e) => {
                    e.preventDefault();
                    form.handleSubmit();
                }}
            >
                <form.AppField name="password">
                    {(field) => <field.FormInput type="password" label="New Password" placeholder="Enter your password" />}
                </form.AppField>

                <form.AppField name="confirmPassword">
                    {(field) => <field.FormInput type="password" label="Confirm Password" placeholder="Enter your password" />}
                </form.AppField>

                <form.AppForm>
                    <form.FormSubmit label="Submit" />
                </form.AppForm>
            </form>

            <p className="text-center text-muted-foreground text-sm">
                <Link href="/signin" className="text-foreground font-medium hover:underline">
                    Back to Login
                </Link>
            </p>
        </div>
    );
}
