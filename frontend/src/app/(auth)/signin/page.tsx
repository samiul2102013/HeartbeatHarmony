"use client";

import { useAppForm } from "@/components/form/form-context";
import { loginAdmin, setAdminSession } from "@/lib/index";
import { useState } from "react";
import { z } from "zod";

const signinSchema = z.object({
    email: z.email("Enter your email address"),
    password: z.string().min(6, "Password must be at least 6 characters").max(32, "Password must be at most 32 characters"),
});

export default function Signin() {
    const [error, setError] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    const form = useAppForm({
        defaultValues: { email: "", password: "" },
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

                <button
                    type="submit"
                    disabled={isLoading}
                    className="h-10 px-4 py-2 rounded-md bg-red-600 text-white font-medium hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isLoading ? "Signing in..." : "Sign In"}
                </button>
            </form>
        </div>
    );
}
