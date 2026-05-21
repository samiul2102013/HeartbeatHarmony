import { cn } from "@/lib/utils";

function Avatar({ className, ...props }: React.ComponentProps<"div">) {
    return <div data-slot="avatar" className={cn("relative flex size-12 shrink-0 overflow-hidden rounded-full", className)} {...props} />;
}

type AvatarImageProps = React.ImgHTMLAttributes<HTMLImageElement> & {
    alt?: string;
};

function AvatarImage({ className, alt = "", ...props }: AvatarImageProps) {
    return (
        <img
            data-slot="avatar-image"
            className={cn("aspect-square size-full object-cover", className)}
            alt={alt}
            {...props}
        />
    );
}

function AvatarFallback({ className, ...props }: React.ComponentProps<"div">) {
    return <div data-slot="avatar-fallback" className={cn("flex size-full items-center justify-center bg-muted text-sm font-medium", className)} {...props} />;
}

export { Avatar, AvatarImage, AvatarFallback };
