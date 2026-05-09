import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Textarea } from "@/components/ui/textarea";
import { useFieldContext } from "./form-context";

type FormTextareaProps = {
    label: string;
    placeholder?: string;
    disabled?: boolean;
};

export function FormTextarea({ label, ...props }: FormTextareaProps) {
    const field = useFieldContext<string>();
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;

    return (
        <Field data-invalid={isInvalid}>
            <FieldLabel htmlFor={field.name}>{label}</FieldLabel>
            <Textarea
                id={field.name}
                rows={6}
                name={field.name}
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                aria-invalid={isInvalid}
                {...props}
            />
            {isInvalid && <FieldError errors={field.state.meta.errors} />}
        </Field>
    );
}
