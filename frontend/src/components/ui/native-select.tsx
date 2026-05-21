import * as React from "react";
import { ChevronDown } from "lucide-react";

import { cn } from "@/lib/utils";

type NativeSelectProps = React.SelectHTMLAttributes<HTMLSelectElement> & {
    containerClassName?: string;
    iconClassName?: string;
};

function NativeSelect({ className, containerClassName, iconClassName, children, ...props }: NativeSelectProps) {
    return (
        <div className={cn("relative", containerClassName)}>
            <select
                className={cn(
                    "h-8 w-full appearance-none rounded-[5px] border border-border bg-background px-3 pr-8 text-[14px] leading-6 text-muted-foreground outline-none",
                    className,
                )}
                {...props}
            >
                {children}
            </select>
            <ChevronDown className={cn("pointer-events-none absolute right-2 top-1/2 size-3 -translate-y-1/2 text-muted-foreground", iconClassName)} />
        </div>
    );
}

export { NativeSelect };
