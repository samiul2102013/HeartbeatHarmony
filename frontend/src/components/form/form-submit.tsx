import { Button } from "@/components/ui/button";
import { useFormContext } from "./form-context";

export function FormSubmit({ label }: { label: string }) {
    const form = useFormContext();

    return (
        <form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
            {([canSubmit, isSubmitting]) => (
                <Button type="submit" className="rounded-md" disabled={!canSubmit}>
                    {label}
                </Button>
            )}
        </form.Subscribe>
    );
}
