import { Button } from "@base-ui/react";
import { Search } from "lucide-react";



export function SearchField({ label, className = "" }: { label: string; className?: string }) {
    return (
        <Button
            type="button"
            className={`flex w-full items-center justify-between rounded-[20px] border border-border bg-background px-5 py-4 text-base leading-normal text-muted-foreground md:text-xl ${className}`}
        >
            <span className="whitespace-nowrap">{label}</span>
            <Search className="size-6 shrink-0 text-muted-foreground" />
        </Button>
    );
}