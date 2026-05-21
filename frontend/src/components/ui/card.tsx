import { cn } from "@/lib/utils";

function Card({ className, ...props }: React.ComponentProps<"div">) {
    return <div data-slot="card" className={cn("rounded-[20px] border border-border bg-card", className)} {...props} />;
}

function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
    return <div data-slot="card-header" className={cn("flex items-center justify-between px-8 pt-6", className)} {...props} />;
}

function CardContent({ className, ...props }: React.ComponentProps<"div">) {
    return <div data-slot="card-content" className={cn("px-8 pb-8", className)} {...props} />;
}

function CardTitle({ className, ...props }: React.ComponentProps<"h3">) {
    return <h3 data-slot="card-title" className={cn("text-4xl font-semibold text-card-foreground", className)} {...props} />;
}

function CardDescription({ className, ...props }: React.ComponentProps<"p">) {
    return <p data-slot="card-description" className={cn("text-xl text-card-foreground", className)} {...props} />;
}

export { Card, CardHeader, CardContent, CardTitle, CardDescription };
