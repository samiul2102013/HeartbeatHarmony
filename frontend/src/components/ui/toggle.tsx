import * as React from "react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface ToggleProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    pressed?: boolean;
    onPressedChange?: (pressed: boolean) => void;
}

export function Toggle({ className, pressed = false, onPressedChange, onClick, children, ...props }: ToggleProps) {
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
        onClick?.(e);
        onPressedChange?.(!pressed);
    };

    return (
        <button
            type="button"
            aria-pressed={pressed}
            data-state={pressed ? "on" : "off"}
            className={cn(
                buttonVariants({ size: "default" }),
                "data-[state=on]:bg-primary data-[state=on]:text-primary-foreground",
                className,
            )}
            onClick={handleClick}
            {...props}
        >
            {children}
        </button>
    );
}
