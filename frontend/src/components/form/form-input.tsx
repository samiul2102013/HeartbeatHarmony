import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useFieldContext } from "./form-context";

type FormInputProps = {
    type?: React.HTMLInputTypeAttribute;
    label: string;
    placeholder?: string;
    disabled?: boolean;
};

export function FormInput({ type = "text", label, ...props }: FormInputProps) {
    const field = useFieldContext<string>();
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;

    return (
        <Field data-invalid={isInvalid}>
            <FieldLabel htmlFor={field.name}>{label}</FieldLabel>
            <Input
                id={field.name}
                type={type}
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
