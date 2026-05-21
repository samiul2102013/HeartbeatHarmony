"use client";

import { useAppForm } from "@/components/form/form-context";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";
import { verifyEmail } from "@/lib/index";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { z } from "zod";

const verifySchema = z.object({
    code: z.string().length(6, "Enter the 6-digit code"),
});

export default function Verify() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const token = searchParams.get("token") || "";

    const form = useAppForm({
        defaultValues: { code: "" },
        validators: { onChange: verifySchema },
        onSubmit: async ({ value }) => {
            await verifyEmail(token || value.code);
            router.push("/reset-password?token=" + (token || value.code));
        },
    });

    return (
        <div className="my-20 mx-auto flex w-full max-w-114 flex-col gap-6 rounded-lg border px-6 py-12">
            <div>
                <h2 className="text-center text-2xl font-bold">Verification</h2>
                <p className="mt-2 text-center text-sm text-muted-foreground">
                    We’ve sent a verification code to your registered email <br />
                    address. Please enter the code below to confirm your <br />
                    identity and continue.
                </p>
            </div>

            <form
                className="grid gap-6"
                onSubmit={(e) => {
                    e.preventDefault();
                    form.handleSubmit();
                }}
            >
                <form.AppField name="code">
                    {(field) => {
                        const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;

                        return (
                            <Field data-invalid={isInvalid}>
                                <FieldLabel htmlFor={field.name}>Enter your OTP</FieldLabel>
                                <InputOTP
                                    id={field.name}
                                    name={field.name}
                                    maxLength={6}
                                    value={field.state.value}
                                    onBlur={field.handleBlur}
                                    onChange={(val) => field.handleChange(val)}
                                    aria-invalid={isInvalid}
                                >
                                    <InputOTPGroup className="mx-auto">
                                        {Array.from({ length: 6 }).map((_, i) => (
                                            <InputOTPSlot key={i} index={i} />
                                        ))}
                                    </InputOTPGroup>
                                </InputOTP>
                                {isInvalid && <FieldError errors={field.state.meta.errors} />}
                            </Field>
                        );
                    }}
                </form.AppField>

                <form.AppForm>
                    <form.FormSubmit label="Verify Code" />
                </form.AppForm>
            </form>

            <p className="text-center text-muted-foreground text-sm">
                Didn't receive the code? Check your email <br />
                and click{" "}
                <Link href="/forgot-password" className="text-red-600 font-medium hover:underline">
                    Resend Code
                </Link>{" "}
                to try again.
            </p>
        </div>
    );
}
