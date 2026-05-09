import { createFormHook, createFormHookContexts } from "@tanstack/react-form";
import { FormImage } from "./form-image";
import { FormInput } from "./form-input";
import { FormSubmit } from "./form-submit";
import { FormTextarea } from "./form-textarea";

export const { fieldContext, formContext, useFormContext, useFieldContext } = createFormHookContexts();

export const { useAppForm } = createFormHook({
    fieldContext,
    formContext,
    fieldComponents: {
        FormInput,
        FormImage,
        FormTextarea,
    },
    formComponents: {
        FormSubmit,
    },
});
