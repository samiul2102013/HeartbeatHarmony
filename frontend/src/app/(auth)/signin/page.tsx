"use client";

import { useAppForm } from "@/components/form/form-context";
import { Checkbox } from "@/components/ui/checkbox";
import { loginAdmin, setAdminSession } from "@/lib/index";
import Link from "next/link";
import { useState } from "react";
import { z } from "zod";

const signinSchema = z.object({
    email: z.email("Enter your email address"),
    password: z.string().min(6, "Password must be at least 6 characters").max(32, "Password must be at most 32 characters"),
    remember: z.boolean(),
});

export default function Signin() {
    const [error, setError] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    const form = useAppForm({
        defaultValues: { email: "", password: "", remember: false },
        validators: { onChange: signinSchema },
        onSubmit: async ({ value }) => {
            try {
                setError("");
                setIsLoading(true);
                const response = await loginAdmin(value.email, value.password);
                setAdminSession(response.access, response.refresh);
                window.location.href = "/";
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : "Login failed. Please try again.";
                setError(errorMessage);
            } finally {
                setIsLoading(false);
            }
        },
    });

    return (
        <div className="my-20 mx-auto flex w-full max-w-150 flex-col gap-6 rounded-lg border px-6 py-12">
            <h2 className="text-center text-2xl font-bold">Sign In</h2>

            <form
                className="grid gap-6"
                onSubmit={(e) => {
                    e.preventDefault();
                    form.handleSubmit();
                }}
            >
                {error && (
                    <div className="p-3 rounded-md bg-red-50 border border-red-200">
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                )}

                <form.AppField name="email">
                    {(field) => <field.FormInput type="email" label="Email" placeholder="Enter your email address" disabled={isLoading} />}
                </form.AppField>

                <form.AppField name="password">
                    {(field) => <field.FormInput type="password" label="Password" placeholder="Enter your password" disabled={isLoading} />}
                </form.AppField>

                <div className="flex items-center justify-between">
                    <form.AppField name="remember">
                        {(field) => (
                            <div className="flex items-center gap-2">
                                <Checkbox
                                    id="remember"
                                    checked={field.state.value}
                                    onCheckedChange={(c) => field.handleChange(c === true)}
                                    disabled={isLoading}
                                />
                                <label htmlFor="remember" className="text-sm text-muted-foreground">
                                    Remember me
                                </label>
                            </div>
                        )}
                    </form.AppField>

                    <Link href="/forgot-password" className="text-primary font-medium hover:underline">
                        Forgot password?
                    </Link>
                </div>

                <button
                    type="submit"
                    disabled={isLoading}
                    className="h-10 px-4 py-2 rounded-md bg-red-600 text-white font-medium hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isLoading ? "Signing in..." : "Sign In"}
                </button>
            </form>

            <p className="text-center text-muted-foreground">
                Do not have account?{" "}
                <Link href="/signup" className="text-foreground font-medium hover:underline">
                    Sign up
                </Link>
            </p>
        </div>
    );
}
