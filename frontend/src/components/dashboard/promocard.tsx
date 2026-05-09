import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { MoreVertical } from "lucide-react";
import Image from "next/image";

interface PromoCardProps {
    title: string;
    description: string;
    image: string;
    status: "active" | "inactive";
    prioritizeImage?: boolean;
}

export function PromoCard({ title, description, image, status, prioritizeImage = false }: PromoCardProps) {
    const normalizedStatus = status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
    const isActive = status === "active";

    return (
        <article className="flex min-h-24 sm:min-h-28 md:min-h-32 w-full overflow-hidden rounded-[10px] bg-background shadow-[0px_12px_40px_-16px_rgba(0,0,0,0.2)] flex-col sm:flex-row">
            <div className="relative h-32 sm:h-36 md:h-40 w-full sm:w-48 md:w-72 sm:shrink-0 overflow-hidden">
                <Image src={image} alt={title} fill loading={prioritizeImage ? "eager" : "lazy"} className="object-cover" />
            </div>

            <div className="flex flex-1 items-start justify-between px-3 sm:px-4 md:px-6 py-2 sm:py-3 md:py-4 gap-3 sm:gap-4">
                <div className="flex flex-col justify-between gap-2 sm:gap-3 md:gap-3">
                    <div className="space-y-0.5 sm:space-y-1">
                        <h3 className="text-xl font-semibold text-foreground">{title}</h3>
                        <p className="text-sm md:text-base text-muted-foreground">{description}</p>
                    </div>

                    <div
                        className={`flex self-start items-center gap-1.5 sm:gap-2 rounded-[10px] ${isActive ? "bg-[#EEFFF5]" : "bg-[#f3f4f6]"} px-2 sm:px-3 py-1.5 sm:py-2`}
                        aria-label={`Status: ${normalizedStatus}`}
                    >
                        {isActive ? (
                            <span className="relative flex h-1.5 w-1.5 sm:h-2 sm:w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-1.5 w-1.5 sm:h-2 sm:w-2 bg-[#22C55E]"></span>
                            </span>
                        ) : (
                            <span className="size-1.5 sm:size-2 rounded-full bg-[#9CA3AF]" aria-hidden="true" />
                        )}
                        <span className={`leading-none text-xs sm:text-sm ${isActive ? "text-[#22C55E]" : "text-[#9CA3AF]"}`}>
                            {normalizedStatus}
                        </span>
                    </div>
                </div>

                <DropdownMenu>
                    <DropdownMenuTrigger className="inline-flex size-5 sm:size-6 md:size-7 items-center justify-center rounded-md text-muted-foreground hover:bg-transparent shrink-0">
                        <MoreVertical className="size-5 sm:size-6 md:size-7" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-40">
                        <DropdownMenuItem>Edit slide</DropdownMenuItem>
                        <DropdownMenuItem>Duplicate</DropdownMenuItem>
                        <DropdownMenuItem variant="destructive">Delete</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </article>
    );
}
