"use client";

import { useAppForm } from "@/components/form/form-context";
import { requestPasswordReset } from "@/lib/index";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { z } from "zod";

const forgotSchema = z.object({
    email: z.email("Enter your email address"),
});

export default function ForgotPassword() {
    const router = useRouter();
    const [submitted, setSubmitted] = useState(false);

    const form = useAppForm({
        defaultValues: { email: "" },
        validators: { onChange: forgotSchema },
        onSubmit: async ({ value }) => {
            await requestPasswordReset(value.email);
            setSubmitted(true);
        },
    });

    return (
        <div className="my-20 mx-auto flex w-full max-w-150 flex-col gap-6 rounded-lg border px-6 py-12">
            <div>
                <h2 className="text-center text-2xl font-bold">Forgot Password</h2>
                <p className="mt-2 text-center text-muted-foreground">
                    Enter your registered email address and we’ll send you a <br />
                    verification code to reset your password.
                </p>
            </div>

            <form
                className="grid gap-6"
                onSubmit={(e) => {
                    e.preventDefault();
                    form.handleSubmit();
                }}
            >
                <form.AppField name="email">
                    {(field) => <field.FormInput type="email" label="Email" placeholder="Enter your email" />}
                </form.AppField>

                <form.AppForm>
                    <form.FormSubmit label="Reset Password" />
                </form.AppForm>
            </form>
        </div>
    );
}
